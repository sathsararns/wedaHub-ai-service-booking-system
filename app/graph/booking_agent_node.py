from app.agents.booking_agent import booking_agent


def booking_agent_node(state):

    booking = booking_agent.invoke(
        {
            "input": state["user_input"]
        }
    ).model_dump()

    requirements = state.get("requirements", {})

    # -----------------------------------------
    # Preserve previous booking values
    # -----------------------------------------

    if not booking.get("date"):
        booking["date"] = requirements.get("date")

    if not booking.get("description"):
        booking["description"] = requirements.get("description")

    # -----------------------------------------
    # Validate selected provider
    # -----------------------------------------

    recommended = state.get("recommended_providers", [])

    selected_index = booking.get("provider_index", -1)

    if selected_index < 0 or selected_index >= len(recommended):
        state["response"] = (
            "❌ Invalid provider number.\n\n"
            "Please select one of the providers shown."
        )
        return state

    recommendation = recommended[selected_index]

    original_index = recommendation["provider_index"]

    providers = state.get("providers", [])

    if original_index < 0 or original_index >= len(providers):
        state["response"] = "❌ Provider could not be found."
        return state

    provider = providers[original_index]

    # -----------------------------------------
    # Save provider
    # -----------------------------------------

    booking["provider_id"] = provider["_id"]
    booking["provider_name"] = (
        f"{provider['firstName']} {provider['lastName']}"
    )

    state["booking"] = booking

    # -----------------------------------------
    # Keep requirements updated
    # -----------------------------------------

    requirements["date"] = booking.get("date")
    requirements["description"] = booking.get("description")

    state["requirements"] = requirements

    return state