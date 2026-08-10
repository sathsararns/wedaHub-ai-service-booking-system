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

    # Previous requirements
    old_requirements = state.get("requirements", {})

    # Newly extracted requirements
    new_requirements = result.model_dump()

    # Merge (only update fields that have values)
    for key, value in new_requirements.items():
        if value not in (None, ""):
            old_requirements[key] = value

    state["requirements"] = old_requirements

    return state