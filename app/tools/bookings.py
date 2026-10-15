"""Request-scoped booking tools; identifiers come from trusted context."""
import logging

from langchain_core.tools import tool

from app.clients.backend_client import backend_client
from app.services.booking_status_service import get_booking_status as fetch_booking_status

logger = logging.getLogger(__name__)


def _extract_booking_id(booking_result):
    """
    booking_create_node.py stores a FLAT dict in state["booking_result"]
    (no nested "booking" key). Still checked defensively in case
    something ever produces the nested {"booking": {...}} shape instead.
    """
    if not isinstance(booking_result, dict):
        return None

    nested = booking_result.get("booking")
    if isinstance(nested, dict):
        nested_id = (
            nested.get("_id")
            or nested.get("bookingId")
            or nested.get("booking_id")
        )
        if nested_id:
            return nested_id

    return (
        booking_result.get("_id")
        or booking_result.get("booking_id")
        or booking_result.get("bookingId")
    )



def make_booking_tools(context: dict, session_id: str | None = None):
    @tool("create_booking")
    def create_booking() -> str:
        """
        Create the booking using the provider, service, city, date and
        description already confirmed earlier in this conversation. Only
        call this once the user has explicitly confirmed the booking
        summary with "yes".
        """

        booking = context.get("booking") or {}
        customer_id = context.get("customer_id")

        logger.info(
            "session=%s TOOL CALL create_booking(provider_id=%s)",
            session_id, booking.get("provider_id"),
        )

        required = ["provider_id", "service", "city", "date", "description"]
        missing = [f for f in required if not booking.get(f)]

        if missing:
            reason = f"Cannot create booking, missing: {', '.join(missing)}."

            logger.warning(
                "session=%s TOOL create_booking rejected, missing=%s",
                session_id, missing,
            )

            context["booking_rejection_reason"] = reason

            return reason

        try:
            result = backend_client.create_booking(
                provider_id=booking["provider_id"],
                customer_id=customer_id,
                service=booking["service"],
                city=booking["city"],
                date=booking["date"],
                description=booking["description"],
                auth_token=context.get("auth_token"),
            )
        except Exception as exc:
            logger.exception("session=%s TOOL create_booking failed", session_id)
            context["booking_error"] = str(exc)
            return f"Booking failed: {exc}"

        context["booking_tool_result"] = result

        logger.info("session=%s TOOL RESULT create_booking -> success", session_id)

        return "Booking created successfully."


    @tool("get_booking_status")
    def get_booking_status() -> str:
        """
        Check the live status of the booking created earlier in this
        conversation.
        """

        booking_id = _extract_booking_id(context.get("booking_result"))

        logger.info(
            "session=%s TOOL CALL get_booking_status(booking_id=%s)",
            session_id, booking_id,
        )

        if not booking_id:
            return "No booking exists yet in this conversation."

        result = fetch_booking_status(booking_id)

        if result.get("success"):
            context["booking_status_result"] = result["booking"]
            logger.info("session=%s TOOL RESULT get_booking_status -> found", session_id)
            return "Booking found."

        logger.warning(
            "session=%s TOOL RESULT get_booking_status -> error=%s",
            session_id, result.get("error"),
        )
        return f"Could not retrieve booking: {result.get('error')}"


    return {"create_booking": create_booking, "get_booking_status": get_booking_status}
