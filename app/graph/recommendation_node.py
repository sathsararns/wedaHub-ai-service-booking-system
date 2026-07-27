from app.agents.requirements_agent import requirements_agent


def requirement_node(state):

    result = requirements_agent.invoke(
        {
            "input": state["user_input"]
        }
    )

    print("===== REQUIREMENTS =====")
    print(result)

    state["requirements"] = result.model_dump()

    return state