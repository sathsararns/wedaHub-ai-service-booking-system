def router(state):
    """
    Decide which node to execute after planner.
    """

    planner = state.get("planner", {})
    action = planner.get("next_action")

    if action == "search_services":
        return "search"

    elif action == "book_provider":
        return "booking"

    elif action == "booking_status":
        return "booking_status"

    elif action == "ask_more_information":
        return "response"

    return "response"