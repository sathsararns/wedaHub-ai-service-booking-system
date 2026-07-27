def response_node(state):

    recommendations = state["recommendations"]["recommendations"]

    message = ""

    for provider in recommendations:

        message += (
            f"Provider : {provider['business_name']}\n"
            f"Reason : {provider['reason']}\n\n"
        )

    state["response"] = message

    return state