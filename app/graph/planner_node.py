from app.agents.planner_agent import planner_agent


def planner_node(state):

    result = planner_agent(state)

    # PlannerDecision model එකක් නම්
    if hasattr(result, "model_dump"):
        state["planner"] = result.model_dump()

    # dict එකක් නම්
    else:
        state["planner"] = result

    return state