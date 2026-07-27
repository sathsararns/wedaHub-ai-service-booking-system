def response_node(state):
    """
    Generates a response message with the list of recommended providers
    and dynamic booking options.
    """
    text = "I found these providers for you:\n\n"
    
    recommendations = state["recommendations"]["recommendations"]
    
    # List all recommendations
    for i, provider in enumerate(recommendations, start=1):
        text += (
            f"{i}. {provider['business_name']}\n"
            f"Reason: {provider['reason']}\n\n"
        )
    
    # Generate dynamic booking reply options
    if recommendations:
        best = recommendations[0]["business_name"]  # Top recommendation
        
        text += (
            f"Reply with:\n"
            f"Book 1\n"
            f"or\n"
            f"Book {best}"
        )
    else:
        text += "No providers found. Please try again with different preferences."
    
    # Store the response in state
    state["response"] = text
    
    return state