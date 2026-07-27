def planner_router(state):

    action = state["planner"]["next_action"]

    if action == "search_services":
        return "search"

    if action == "book_provider":
        return "booking_agent"

    return "response"