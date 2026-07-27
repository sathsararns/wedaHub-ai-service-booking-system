def response_node(state):
    """
    Generates a response message with either:
    - List of recommended providers with dynamic booking options, OR
    - Booking confirmation if a booking was just made
    """
    
    # Check if we just completed a booking
    booking = state.get("booking_result")
    
    if booking:
        # Handle successful booking
        state["response"] = (
            "✅ Booking created successfully!\n\n"
            f"Booking ID: {booking['_id']}\n"
            f"Provider: {booking.get('provider_name', 'N/A')}\n"
            f"Date/Time: {booking.get('datetime', 'N/A')}\n\n"
            "Thank you for using our service!"
        )
        return state
    
    # Check if there was a booking error
    booking_error = state.get("booking_error")
    if booking_error:
        state["response"] = (
            "❌ Booking failed!\n\n"
            f"Error: {booking_error}\n\n"
            "Please try again or contact support."
        )
        return state
    
    # Handle recommendations (original logic)
    recommendations = state.get("recommendations", {}).get("recommendations", [])
    
    if not recommendations:
        state["response"] = (
            "No providers found. Please try again with different preferences.\n"
            "You can adjust:\n"
            "- Location\n"
            "- Service type\n"
            "- Budget range"
        )
        return state
    
    # Build response with recommendations
    text = "I found these providers for you:\n\n"
    
    for i, provider in enumerate(recommendations, start=1):
        text += (
            f"{i}. {provider.get('business_name', 'Unknown')}\n"
            f"   Reason: {provider.get('reason', 'No reason provided')}\n"
            f"   Rating: {provider.get('rating', 'N/A')} ⭐\n\n"
        )
    
    # Generate dynamic booking reply options
    if recommendations:
        best = recommendations[0].get("business_name", "Provider 1")
        
        # Create dynamic booking options
        text += (
            "📅 Reply with:\n"
            f"  • 'Book 1' - Book the top provider\n"
            f"  • 'Book {best}' - Book {best} directly\n"
        )
        
        # Add additional options if there are more providers
        if len(recommendations) > 1:
            for i, provider in enumerate(recommendations[1:], start=2):
                text += f"  • 'Book {i}' - Book {provider.get('business_name', f'Provider {i}')}\n"
        
        text += "\nOr reply with 'More options' to see alternatives."
    
    state["response"] = text
    return state