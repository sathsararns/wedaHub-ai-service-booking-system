from app.agents.booking_agent import booking_agent

def booking_agent_node(state):

    booking = booking_agent.invoke(
        {
            "input": state["user_input"]
        }
    )

    state["booking"] = booking.model_dump()

    return state