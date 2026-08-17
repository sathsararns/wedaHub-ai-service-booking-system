def router(state):
    """
    Decide which node to execute after planner.
    """

    planner = state.get("planner", {})
    action = planner.get("next_action")

    print("\n===== ROUTER =====")
    print("Planner :", planner)
    print("Action  :", action)

    if action == "search_services":
        return "search"

    elif action == "book_provider":
        return "booking"

    elif action == "booking_status":
        return "booking_status"

    elif action == "ask_login":
        return "response"

    elif action == "ask_more_information":
        return "response"

    print("Unknown action. Routing to response.")
    return "response"


def booking_router(state):
    """
    Decide whether booking can be created
    or more booking information is required.
    """

    booking = state.get("booking")

    print("\n===== BOOKING ROUTER =====")
    print("Booking :", booking)

    # No booking information
    if not booking:
        state["response"] = (
            "❌ I couldn't find the provider you selected."
        )
        return "response"

    # ------------------------------------------------
    # DATE REQUIRED
    # ------------------------------------------------

    if not booking.get("date"):

        state["response"] = (
            "📅 What date and time would you like to book?\n\n"
            "Examples:\n"
            "• Tomorrow 10 AM\n"
            "• Friday 2 PM\n"
            "• 15 August 9:30 AM"
        )

        return "response"

    # ------------------------------------------------
    # Everything required is available
    # ------------------------------------------------

    return "booking"