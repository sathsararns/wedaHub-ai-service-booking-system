from app.agents.booking_agent import booking_agent


def booking_agent_node(state):

    booking = booking_agent.invoke(
        {
            "input": state["user_input"]
        }
    ).model_dump()

    # Check if date and time are missing from booking
    if not booking["date"]:
        booking["date"] = state["requirements"]["date"]

    if not booking["time"]:
        booking["time"] = state["requirements"]["time"]

    # Get provider details from recommended providers
    provider = state["recommended_providers"][
        booking["provider_index"]
    ]

    booking["provider_id"] = provider["provider_id"]
    booking["provider_name"] = provider["provider_name"]

    state["booking"] = booking

    return state