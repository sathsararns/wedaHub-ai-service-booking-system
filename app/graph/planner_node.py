from app.agents.planner_agent import planner_agent


def planner_node(state):
    """
    Decide the next action.

    Priority:
    1. Continue an active booking flow.
    2. Otherwise use the planner agent.
    """

    booking = state.get("booking") or {}

    # -----------------------------------------
    # Continue existing booking flow
    # -----------------------------------------
    if booking.get("provider_id"):

        # Ask for date
        if not booking.get("date"):
            state["planner"] = {
                "next_action": "book_provider",
                "missing_fields": ["date"],
                "message": "Continue booking.",
            }
            return state

        # Ask for description
        if not booking.get("description"):
            state["planner"] = {
                "next_action": "book_provider",
                "missing_fields": ["description"],
                "message": "Continue booking.",
            }
            return state

        # Booking has all required information
        state["planner"] = {
            "next_action": "book_provider",
            "missing_fields": None,
            "message": "Creating booking.",
        }
        return state

    # -----------------------------------------
    # Normal planner
    # -----------------------------------------
    result = planner_agent(state)

    print("===== PLANNER RESULT =====")
    print(result)

    if hasattr(result, "model_dump"):
        state["planner"] = result.model_dump()
    else:
        state["planner"] = result

    return state