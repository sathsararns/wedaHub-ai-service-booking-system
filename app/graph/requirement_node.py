from app.agents.requirements_agent import requirements_agent


def requirement_node(state):

    message = state["user_input"].lower().strip()

    booking = state.get("booking") or {}

    # ---------------------------------------
    # Don't extract requirements while booking
    # ---------------------------------------

    if booking.get("provider_id"):
        return state

    if message.startswith("book"):
        return state

    result = requirements_agent.invoke(
        {
            "input": state["user_input"]
        }
    )

    print(result)

    old_requirements = state.get("requirements", {})

    new_requirements = result.model_dump()

    for key, value in new_requirements.items():
        if value not in (None, ""):
            old_requirements[key] = value

    state["requirements"] = old_requirements

    return state