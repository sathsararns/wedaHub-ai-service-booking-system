def response_node(state):

    text = "I found these providers for you:\n\n"

    for i, provider in enumerate(state["recommendations"]["recommendations"], start=1):

        text += (
            f"{i}. {provider['business_name']}\n"
            f"Reason: {provider['reason']}\n\n"
        )

    text += "Reply with:\nBook 1\nor\nBook ABC Electrical"

    state["response"] = text

    return state