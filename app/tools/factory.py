"""Build tools for one chat turn; no context is shared between requests."""
from app.tools.bookings import make_booking_tools
from app.tools.providers import make_provider_tools


def make_tools(context: dict, session_id: str | None = None):
    return {
        **make_provider_tools(context, session_id),
        **make_booking_tools(context, session_id),
    }
