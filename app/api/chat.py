import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
from app.models.chat import ChatRequest, ResetRequest
from app.services.chat_service import chat, clear_chat_session

logger = logging.getLogger(__name__)

router = APIRouter()


def _created_booking(result):
    """Expose a booking card only after the backend created a real booking."""
    if not result.get("booking_created"):
        return None
    booking = result.get("booking_result")
    if not isinstance(booking, dict):
        return None
    booking_id = (
        booking.get("booking_id") or booking.get("bookingId")
        or booking.get("_id") or booking.get("id")
    )
    return booking if booking_id and booking_id != "-" else None


@router.post("/chat")
async def chat_api(request: ChatRequest):
    result = await run_in_threadpool(
        chat,
        session_id=request.session_id or request.customer_id or "guest",
        customer_id=request.customer_id,
        user_input=request.message,
    )

    return {
        "response": result.get("response"),
        "recommendations": result.get("recommended_providers", []),
        "booking": _created_booking(result),
    }


def _chunk_words(text, group_size=4):
    """
    Splits already-complete text into small groups of words (preserving
    exact whitespace — concatenating every chunk reproduces `text`
    exactly) so a real HTTP stream has more than one frame to send.
    No delay is inserted between chunks; they're written as fast as the
    event loop can flush them.
    """
    words = text.split(" ")

    for i in range(0, len(words), group_size):
        chunk = " ".join(words[i:i + group_size])

        if i + group_size < len(words):
            chunk += " "

        yield chunk


async def _stream_chat_response(session_id, customer_id, user_input):
    """
    Streams the chat reply over a real HTTP connection (Server-Sent
    Events framing) instead of returning it as one blocking JSON payload
    for the frontend to fake-type out.

    Important honesty note: response_node.py builds the final reply with
    plain Python string formatting, not a live LLM generation call — the
    LLM calls inside the requirements/planner/recommendation nodes have
    already finished by the time this text exists, so there is no live
    token stream to relay for the reply text itself. What this endpoint
    streams is the real, already-known text, sent over a real transport
    in real chunks with no injected delay — genuine network streaming of
    a known string, not token-by-token LLM generation. See README.md,
    section "Streaming", for the full explanation.
    """

    logger.info("session=%s stream requested", session_id)

    # Flush headers before the workflow starts, and keep health checks responsive
    # while synchronous model/backend calls are running.
    yield ": connected\n\n"
    try:
        result = await run_in_threadpool(
            chat,
            session_id=session_id,
            customer_id=customer_id,
            user_input=user_input,
        )
    except Exception:
        logger.exception("session=%s chat stream failed", session_id)
        frame = json.dumps({
            "type": "error",
            "message": "The AI assistant could not finish your request. Please try again shortly.",
        })
        yield f"data: {frame}\n\n"
        return

    response_text = result.get("response") or ""

    chunk_count = 0

    for chunk in _chunk_words(response_text):
        chunk_count += 1
        frame = json.dumps({"type": "chunk", "text": chunk})
        yield f"data: {frame}\n\n"

    done_frame = json.dumps(
        {
            "type": "done",
            "recommendations": result.get("recommended_providers", []),
            "booking": _created_booking(result),
        }
    )
    yield f"data: {done_frame}\n\n"

    logger.info("session=%s stream finished, chunks_sent=%d", session_id, chunk_count)


@router.post("/chat/stream")
async def chat_stream_api(request: ChatRequest):
    session_id = request.session_id or request.customer_id or "guest"

    return StreamingResponse(
        _stream_chat_response(session_id, request.customer_id, request.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat/reset")
async def reset_chat(request: ResetRequest):
    session_id = request.session_id or request.customer_id or "guest"
    clear_chat_session(session_id)
    return {"message": "chat reset", "sessionId": session_id}
