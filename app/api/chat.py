from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.services.chat_service import chat
from app.memory.memory import memory

router = APIRouter()


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    customer_id: str | None = Field(default=None, alias="customerId")
    session_id: str | None = Field(default=None, alias="sessionId")


class ResetRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str | None = Field(default=None, alias="customerId")
    session_id: str | None = Field(default=None, alias="sessionId")


@router.post("/chat")
async def chat_api(request: ChatRequest):
    result = chat(
        session_id=request.session_id or request.customer_id or "guest",
        customer_id=request.customer_id,
        user_input=request.message,
    )

    booking = result.get("booking")
    if not booking or (isinstance(booking, dict) and len(booking) == 0):
        booking = None

    return {
        "response": result.get("response"),
        "recommendations": result.get("recommended_providers", []),
        "booking": booking,
    }


@router.post("/chat/reset")
async def reset_chat(request: ResetRequest):
    session_id = request.session_id or request.customer_id or "guest"
    memory.clear(session_id)
    return {"message": "chat reset", "sessionId": session_id}