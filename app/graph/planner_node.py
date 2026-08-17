from app.agents.planner_agent import planner_agent


def planner_node(state):
    """
    Planner node.

    Responsible only for deciding the next workflow.
    """

    print("\n===== PLANNER INPUT STATE =====")
    print(state)

    # ------------------------------------------
    # Clear stale booking state
    # ------------------------------------------

    state.pop("booking_error", None)
    state.pop("booking_result", None)
    state.pop("booking_status", None)

    # ------------------------------------------
    # Get planner decision
    # ------------------------------------------

    result = planner_agent(state)

    print("\n===== PLANNER RESULT =====")
    print(result)

    # ------------------------------------------
    # Save planner output
    # ------------------------------------------

    if hasattr(result, "model_dump"):
        state["planner"] = result.model_dump()
    else:
        state["planner"] = result

    return state