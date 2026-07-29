from app.agents.requirements_agent import requirements_agent


def requirement_node(state):

    message = state["user_input"].lower().strip()

    # DON'T overwrite requirements while booking
    if message.startswith("book"):
        return state

    result = requirements_agent.invoke(
        {
            "input": state["user_input"]
        }
    )

    print(result)

    state["requirements"] = result.model_dump()

    return state