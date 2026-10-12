"""
Booking creation, via LLM tool-calling.

booking_agent_node.py and booking_confirmation_node.py (both unchanged)
do all the deterministic slot-filling and yes/no confirmation parsing —
by the time this node runs, booking_router has already verified every
required field is present and the user has said "yes". What used to be
a direct, unconditional call to backend_client.create_booking() is now
delegated to an LLM holding exactly one tool, create_booking(). The
tool itself re-validates every required field and refuses if any is
actually missing (defence in depth: the shape/formatting logic below is
unchanged from before this refactor, only its *source* — a tool result
instead of a direct call — is new).
"""

from __future__ import annotations

import logging

from app.core.tracing import trace_node
from app.agents.tool_runner import run_tool_agent
from app.tools.factory import make_tools

logger = logging.getLogger(__name__)

from app.prompts.booking_create_prompt import BOOKING_CREATE_PROMPT


def _clean_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value


def _extract_booking_data(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}

    booking = result.get("booking")
    if isinstance(booking, dict) and booking:
        return booking

    if any(k in result for k in ["_id", "bookingId", "providerId", "provider_id"]):
        return result

    return {}


@trace_node("booking_create_node")
def booking_create_node(state):
    session_id = state.get("session_id")

    booking = dict(state.get("booking") or {})

    context = {
        "booking": booking,
        "customer_id": state.get("customer_id"),
        "auth_token": state.get("auth_token"),
    }

    tools = make_tools(context, session_id=session_id)
    create_tools = [tools["create_booking"]]

    called = run_tool_agent(
        session_id,
        BOOKING_CREATE_PROMPT,
        "The user has confirmed the booking summary. Create the booking now.",
        create_tools,
    )

    logger.info("session=%s tools_called=%s", session_id, called)

    # ---------------------------------------------------------
    # The tool itself refused (missing fields) or the backend call raised
    # ---------------------------------------------------------
    failure_reason = context.get("booking_rejection_reason") or context.get("booking_error")

    if failure_reason:
        state["booking_status"] = "failed"
        state["booking_error"] = failure_reason
        state["response"] = f"❌ Booking Failed\n\n{failure_reason}"
        state["booking_created"] = False
        state["planner"] = {"next_action": "response"}
        return state

    result = context.get("booking_tool_result")

    if not result:
        # The agent didn't call the tool at all — fail safely rather than
        # silently pretending the booking succeeded.
        logger.warning("session=%s agent did not call create_booking", session_id)
        state["booking_status"] = "failed"
        state["booking_error"] = "Booking agent did not create the booking."
        state["response"] = "❌ Booking Failed\n\nPlease try again."
        state["booking_created"] = False
        state["planner"] = {"next_action": "response"}
        return state

    if not isinstance(result, dict):
        result = {}

    created_booking = _extract_booking_data(result)

    booking_id = (
        created_booking.get("_id")
        or created_booking.get("bookingId")
        or created_booking.get("id")
        or created_booking.get("booking_id")
        or result.get("bookingId")
        or result.get("booking_id")
    )

    status = (
        created_booking.get("status")
        or result.get("status")
        or "Pending"
    )

    final_booking = {
        "provider_index": booking.get("provider_index"),
        "provider_id": booking.get("provider_id"),
        "provider_name": booking.get("provider_name"),
        "service": _clean_text(booking.get("service")),
        "city": _clean_text(booking.get("city")),
        "date": _clean_text(booking.get("date")),
        "description": _clean_text(booking.get("description")),
        "booking_id": booking_id,
        "status": status,
    }

    final_booking["providerName"] = final_booking["provider_name"]
    final_booking["serviceName"] = final_booking["service"]
    final_booking["bookingId"] = booking_id
    final_booking["bookingStatus"] = status

    state["booking_result"] = final_booking
    state["booking"] = final_booking
    state["booking_status"] = "success"
    state.pop("booking_error", None)
    state["booking_created"] = True

    # Keep booking ID in state if needed later, but DO NOT show it in chat text
    state["created_booking"] = final_booking
    state["booking_card"] = final_booking

    lines = [
        "✅ Booking Created Successfully!",
        "",
        f"Provider : {final_booking.get('provider_name', 'Provider')}",
        f"Service : {final_booking.get('service', '')}",
        f"City : {final_booking.get('city', '')}",
        f"Date : {final_booking.get('date', '')}",
        f"Description : {final_booking.get('description', '')}",
        f"Status : {final_booking.get('status', 'Pending')}",
    ]

    state["response"] = "\n".join(lines)
    state["planner"] = {"next_action": "finish"}

    logger.info("session=%s booking created, booking_id=%s", session_id, booking_id)

    return state
