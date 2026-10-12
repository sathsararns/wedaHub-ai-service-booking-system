"""
Booking status lookup, via LLM tool-calling.

Replaces the old booking_status_agent.py -> booking_status_tool.py chain
(both deleted — that logic moved into
app.tools.factory.get_booking_status, called here through the same
tool-agent mechanism used by the search/recommend and booking-create
nodes). booking_id is never an LLM-supplied argument — see
bookings.py for why.
"""

import logging

from app.core.tracing import trace_node
from app.agents.tool_runner import run_tool_agent
from app.tools.factory import make_tools

logger = logging.getLogger(__name__)

from app.prompts.booking_status_prompt import BOOKING_STATUS_PROMPT


@trace_node("booking_status_node")
def booking_status_node(state):
    session_id = state.get("session_id")

    context = {
        "booking_result": state.get("booking_result"),
    }

    tools = make_tools(context, session_id=session_id)
    status_tools = [tools["get_booking_status"]]

    called = run_tool_agent(
        session_id,
        BOOKING_STATUS_PROMPT,
        "Check my booking status.",
        status_tools,
    )

    logger.info("session=%s tools_called=%s", session_id, called)

    booking = context.get("booking_status_result")

    if not booking:

        logger.warning("session=%s no booking status found", session_id)

        state["response"] = (
            "❌ No booking found."
        )

        return state

    state["booking_status"] = booking

    logger.info(
        "session=%s booking status found, booking_id=%s status=%s",
        session_id,
        booking.get("_id"),
        booking.get("status"),
    )

    # --------------------------------
    # Provider Details
    # --------------------------------
    provider = booking.get("providerId")

    provider_name = "Unknown"

    if isinstance(provider, dict):

        provider_name = (
            f"{provider.get('firstName', '')} "
            f"{provider.get('lastName', '')}"
        ).strip()

    # --------------------------------
    # Date
    # --------------------------------
    booking_date = booking.get("date", "")

    if booking_date:
        booking_date = booking_date[:10]

    # --------------------------------
    # Response
    # --------------------------------
    state["response"] = (
        "📅 Booking Status\n\n"
        f"Booking ID : {booking.get('_id')}\n"
        f"Provider : {provider_name}\n"
        f"Service : {booking.get('serviceName')}\n"
        f"Date : {booking_date}\n"
        f"Description : {booking.get('description')}\n"
        f"Status : {booking.get('status')}"
    )

    return state
