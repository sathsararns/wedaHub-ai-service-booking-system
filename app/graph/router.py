def router(state):
    """
    Decide which node to execute after planner.
    """

    planner = state.get("planner") or {}
    action = planner.get("next_action", "")

    print("\n========== ROUTER ==========")
    print("Planner :", planner)
    print("Action  :", action)

    routes = {
        "search_services": "search",

        "book_provider": "booking",

        "await_confirmation": "booking",

        "confirm_booking": "booking",

        "create_booking": "booking",

        "booking_status": "booking_status",

        "ask_login": "response",

        "ask_more_information": "response",

        "general_chat": "response",

        "response": "response",

        "stop": "response",
    }

    next_node = routes.get(action)

    if next_node:
        return next_node

    print("Unknown planner action :", action)

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

    booking = state.get("booking") or {}
    planner = state.get("planner") or {}

    action = planner.get("next_action", "")

    print("\n========== BOOKING ROUTER ==========")
    print("Planner :", planner)
    print("Booking :", booking)

    # --------------------------------------------------
    # No booking
    # --------------------------------------------------

    if not booking:

        state["response"] = (
            "❌ I couldn't identify the booking details."
        )

        return "response"

    # --------------------------------------------------
    # Provider required
    # --------------------------------------------------

    if not booking.get("provider_id"):

        state["response"] = (
            "Please select a provider first."
        )

        return "response"

    # --------------------------------------------------
    # Service required
    # --------------------------------------------------

    if not booking.get("service"):

        state["response"] = (
            "What service would you like to book?"
        )

        return "response"

    # --------------------------------------------------
    # Date required
    # --------------------------------------------------

    if not booking.get("date"):

        state["response"] = (
            "📅 What date would you like to book?\n\n"
            "Examples:\n"
            "• Tomorrow\n"
            "• Next Monday\n"
            "• 2026-08-20"
        )

        return "response"

    # --------------------------------------------------
    # Description required
    # --------------------------------------------------

    if not booking.get("description"):

        state["response"] = (
            "📝 Please briefly describe the work you need done."
        )

        return "response"

    # --------------------------------------------------
    # Planner requested create
    # --------------------------------------------------

    if action == "create_booking":
        return "create"

    # --------------------------------------------------
    # Already confirmed
    # --------------------------------------------------

    if state.get("booking_confirmed"):
        return "create"

    # --------------------------------------------------
    # Planner requested confirmation
    # --------------------------------------------------

    if action in (
        "await_confirmation",
        "confirm_booking",
    ):
        return "confirm"

    # --------------------------------------------------
    # Default
    # --------------------------------------------------

    return "confirm"