import logging

logger = logging.getLogger(__name__)


def router(state):
    """
    Decide which node to execute after planner.
    """

    session_id = state.get("session_id")
    planner = state.get("planner") or {}
    action = planner.get("next_action", "")

    logger.info("session=%s router action=%s", session_id, action)

    routes = {
        # Search
        "search_services": "search",

        # Booking
        "book_provider": "booking",
        "await_confirmation": "booking",
        "confirm_booking": "booking",
        "create_booking": "booking",

        # Status
        "booking_status": "booking_status",

        # Response
        "ask_login": "response",
        "ask_more_information": "response",
        "general_chat": "response",
        "response": "response",
        "stop": "response",
    }

    next_node = routes.get(action)

    if next_node:
        return next_node

    logger.warning("session=%s unknown planner action=%s", session_id, action)

    return "response"


def booking_router(state):
    """
    Booking workflow router.

        booking_agent
             ↓
    booking_confirmation
             ↓
     booking_create
             ↓
         response
    """

    session_id = state.get("session_id")
    planner = state.get("planner") or {}
    booking = state.get("booking") or {}

    action = planner.get("next_action", "")

    logger.info("session=%s booking_router action=%s", session_id, action)

    # ---------------------------------------
    # No booking
    # ---------------------------------------

    if not booking:

        state["response"] = (
            "❌ I couldn't identify the booking details."
        )

        return "response"

    # ---------------------------------------
    # Provider required
    # ---------------------------------------

    if not booking.get("provider_id"):

        state["response"] = (
            "Please select a provider first."
        )

        return "response"

    # ---------------------------------------
    # Service required
    # ---------------------------------------

    if not booking.get("service"):

        state["response"] = (
            "What service would you like to book?"
        )

        return "response"

    # ---------------------------------------
    # Date required
    # ---------------------------------------

    if not booking.get("date"):

        state["response"] = (
            "📅 What date would you like to book?\n\n"
            "Examples:\n"
            "• Tomorrow\n"
            "• Next Monday\n"
            "• 2026-08-20"
        )

        return "response"

    # ---------------------------------------
    # Description required
    # ---------------------------------------

    if not booking.get("description"):

        state["response"] = (
            "📝 Please briefly describe the work you need done."
        )

        return "response"

    # ---------------------------------------
    # Already confirmed
    # ---------------------------------------

    if state.get("booking_confirmed"):

        logger.info("session=%s booking already confirmed -> create", session_id)

        return "create"

    # ---------------------------------------
    # Planner requested create
    # ---------------------------------------

    if action == "create_booking":

        logger.info("session=%s planner requested booking creation", session_id)

        return "create"

    # ---------------------------------------
    # Need confirmation
    # ---------------------------------------

    logger.info("session=%s needs booking confirmation", session_id)

    return "confirm"