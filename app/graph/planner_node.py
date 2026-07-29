from app.agents.planner_agent import planner_agent


def planner_node(state):

    message = state["user_input"].lower().strip()

    # User typed "Book ..."
    if message.startswith("book"):
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