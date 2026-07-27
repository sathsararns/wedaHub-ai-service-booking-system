from app.agents.booking_executor import booking_executor


def booking_node(state):

    booking = state["booking"]

    provider = state["providers"][booking["provider_index"]]

    result = booking_executor(

        state["requirements"],

        provider

    )

    state["booking_result"] = result

    return state