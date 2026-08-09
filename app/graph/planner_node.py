from app.agents.planner_agent import planner_agent


def planner_node(state):

    result = planner_agent(state)

    print("===== PLANNER RESULT =====")
    print(result)

    if hasattr(result, "model_dump"):
        state["planner"] = result.model_dump()
    else:
        state["planner"] = result

    return state