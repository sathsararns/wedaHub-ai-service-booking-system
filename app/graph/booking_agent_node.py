from app.agents.booking_agent import booking_agent


def booking_agent_node(state):

    booking = booking_agent.invoke(
        {
            "input": state["user_input"]
        }
    ).model_dump()

    requirements = state.get("requirements", {})

    # Fill missing date
    if not booking.get("date"):
        booking["date"] = requirements.get("date", "")

    # Fill missing description
    if not booking.get("description"):
        booking["description"] = requirements.get("description", "")

    providers = state.get("recommended_providers", [])

    index = booking.get("provider_index", -1)

    # Validate provider index
    if index < 0 or index >= len(providers):
        state["response"] = (
            "❌ Invalid provider number.\n\n"
            "Please select one of the providers shown."
        )
        return state

    provider = providers[index]

    booking["provider_id"] = provider["provider_id"]
    booking["provider_name"] = provider["provider_name"]

    state["booking"] = booking

    return state