def planner_router(state):

    action = state["planner"]["next_action"]

    if action == "search_services":
        return "search"

    elif action == "book_provider":
        return "booking_agent"

    else:
        return "response"