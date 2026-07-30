def response_node(state):
    """
    Generates a response message with either:
    - Recommended providers
    - Booking confirmation
    - Booking error
    """

    # -----------------------------
    # Booking Success
    # -----------------------------
    booking_result = state.get("booking_result")

    if booking_result:

        booking = booking_result["booking"]

        provider = booking.get("providerId", {})

        provider_name = (
            f"{provider.get('firstName', '')} "
            f"{provider.get('lastName', '')}"
        ).strip()

        state["response"] = (
            "✅ Booking Created Successfully!\n\n"
            f"Booking ID : {booking['_id']}\n"
            f"Provider : {provider_name}\n"
            f"Service : {booking['serviceName']}\n"
            f"Description : {booking.get('description', '-')}\n"
            f"Date : {booking['date'][:10]}\n"
            f"Status : {booking['status']}"
        )

        return state

    # -----------------------------
    # Booking Error
    # -----------------------------
    booking_error = state.get("booking_error")

    if booking_error:

        state["response"] = (
            "❌ Booking Failed!\n\n"
            f"{booking_error}\n\n"
            "Please try again."
        )

        return state

    # -----------------------------
    # Recommendations
    # -----------------------------
    recommendations = (
        state.get("recommendations", {})
        .get("recommendations", [])
    )

    if not recommendations:

        state["response"] = (
            "No providers found.\n\n"
            "Try changing:\n"
            "- Service\n"
            "- Location\n"
            "- Budget"
        )

        return state

    text = "I found these providers for you:\n\n"

    for i, provider in enumerate(recommendations, start=1):

        text += (
            f"{i}. {provider.get('business_name', 'Unknown')}\n"
            f"   Reason : {provider.get('reason', '')}\n"
            f"   Rating : {provider.get('rating', 'N/A')} ⭐\n\n"
        )

    best = recommendations[0].get(
        "business_name",
        "Provider 1"
    )

    text += (
        "📅 Reply with:\n"
        "• Book 1\n"
        f"• Book {best}\n"
    )

    if len(recommendations) > 1:

        for i, provider in enumerate(
            recommendations[1:],
            start=2,
        ):

            text += (
                f"• Book {i} - "
                f"{provider.get('business_name', f'Provider {i}')}\n"
            )

    text += "\nOr reply with 'More options'."

    state["response"] = text

    return state