from app.agents.booking_agent import booking_agent


def booking_agent_node(state):

    result = booking_agent.invoke(

        {
            "input": state["user_input"]
        }

    )

    state["booking"] = result

    return state