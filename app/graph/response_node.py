def response_node(state):
    """
    Generates the final response.
    """

    planner = state.get("planner", {})

    # =====================================================
    # Ask More Information
    # =====================================================

    if planner.get("next_action") == "ask_more_information":

        missing = planner.get("missing_fields", [])

        questions = []

        if "date" in missing:
            questions.append("📅 What date would you like to book?")

        if "description" in missing:
            questions.append("📝 Please describe the work you need.")

        if "service" in missing:
            questions.append("🔧 What service do you need?")

        if "location" in missing:
            questions.append("📍 Which location do you need the service in?")

        state["response"] = "\n".join(questions)

        return state

    # =====================================================
    # Booking Success
    # =====================================================

    booking_result = state.get("booking_result")

    if booking_result:

        booking = booking_result.get("booking", {})

        provider = booking.get("providerId", {})

        provider_name = (
            f"{provider.get('firstName', '')} "
            f"{provider.get('lastName', '')}"
        ).strip()

        state["response"] = (
            "✅ Booking Created Successfully!\n\n"
            f"Booking ID : {booking.get('_id', '-')}\n"
            f"Provider : {provider_name}\n"
            f"Service : {booking.get('serviceName', '-')}\n"
            f"Description : {booking.get('description', '-')}\n"
            f"Date : {str(booking.get('date', ''))[:10]}\n"
            f"Status : {booking.get('status', '-')}"
        )

        return state

    # =====================================================
    # Booking Error
    # =====================================================

    booking_error = state.get("booking_error")

    if booking_error:

        state["response"] = (
            "❌ Booking Failed!\n\n"
            f"{booking_error}"
        )

        return state

    # =====================================================
    # Recommendations
    # =====================================================

    recommendation_data = state.get("recommendations", {})

    recommendations = recommendation_data.get("recommendations", [])

    state["recommended_providers"] = recommendations

    if not recommendations:

        state["response"] = (
            "No providers found.\n\n"
            "Try changing:\n"
            "- Service\n"
            "- Location"
        )

        return state

    # =====================================================
    # Recommendation List
    # =====================================================

    text = "I found these providers for you:\n\n"

    for i, provider in enumerate(recommendations, start=1):

        text += (
            f"{i}. {provider.get('business_name', 'Unknown')}\n"
            f"   Reason : {provider.get('reason', '')}\n"
            f"   Rating : {provider.get('rating', 'N/A')} ⭐\n\n"
        )

    text += "📅 Reply with:\n"

    for i, provider in enumerate(recommendations, start=1):
        text += f"• Book {i} - {provider.get('business_name')}\n"

    text += "\nOr reply with 'More options'."

    state["response"] = text

    return state