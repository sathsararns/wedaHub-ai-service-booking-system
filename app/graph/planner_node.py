from app.agents.planner_agent import planner_agent


def planner_node(state):

    if state.get("booking"):

        state["planner"] = {
            "next_action": "book_provider"
        }

        return state

    result = planner_agent.invoke(
        {
            "requirements": str(state["requirements"])
        }
    )

    state["planner"] = result.model_dump()

    return state