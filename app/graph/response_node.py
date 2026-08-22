def response_node(state):
    """
    Generate final response for user.
    """

    # ==========================================
    # Helper
    # ==========================================

    def respond(text):
        state["response"] = text
        return state

    planner = state.get("planner") or {}
    requirements = state.get("requirements") or {}
    booking = state.get("booking") or {}

    if not isinstance(planner, dict):
        planner = {}

    if not isinstance(requirements, dict):
        requirements = {}

    if not isinstance(booking, dict):
        booking = {}

    action = planner.get("next_action", "")

    user = (
        state.get("user_input", "")
        .strip()
        .lower()
    )

    state["booking_created"] = False

    # ==========================================
    # Booking Success
    # ==========================================

    if state.get("booking_status") == "success":

        result = state.get("booking_result") or {}

        booking_id = (
            result.get("_id")
            or result.get("bookingId")
            or result.get("id")
            or "-"
        )

        provider = booking.get(
            "provider_name",
            "Provider"
        )

        service = booking.get(
            "service",
            "-"
        )

        city = booking.get(
            "city",
            "-"
        )

        date = booking.get(
            "date",
            "-"
        )

        description = booking.get(
            "description",
            "-"
        )

        state["booking_created"] = True

        state["created_booking"] = {
            "_id": booking_id,
            "providerName": provider,
            "serviceName": service,
            "city": city,
            "date": date,
            "description": description,
            "status": "Pending",
        }

        state["booking_card"] = (
            state["created_booking"].copy()
        )

        return respond(
            "✅ Booking Created Successfully!\n\n"
            f"Booking ID : {booking_id}\n"
            f"Provider : {provider}\n"
            f"Service : {service}\n"
            f"City : {city}\n"
            f"Date : {date}\n"
            f"Description : {description}\n"
            "Status : Pending"
        )

    # ==========================================
    # Booking Error
    # ==========================================

    booking_error = state.get("booking_error")

    if booking_error:

        return respond(
            f"❌ Booking Failed\n\n{booking_error}"
        )

    # ==========================================
    # Greetings
    # ==========================================

    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "good morning",
        "good afternoon",
        "good evening",
    }

    if user in greetings:

        return respond(
            "👋 Welcome to WedaHub.\n\n"
            "Tell me:\n\n"
            "🔧 What service do you need?\n"
            "📍 Which city?\n\n"
            "Example:\n"
            "• I need a plumber in Galle\n"
            "• I need an electrician in Matara"
        )

    thanks = {
        "thanks",
        "thank you",
        "thx",
    }

    if user in thanks:

        return respond(
            "😊 You're welcome!"
        )

    # ==========================================
    # Login Required
    # ==========================================

    if action == "ask_login":

        return respond(
            "🔒 Please login first to create a booking."
        )
        # ==========================================
    # SEARCH RESULTS
    # ==========================================

    if action == "search_services":

        recommendation_data = (
            state.get("recommendations") or {}
        )

        recommendations = recommendation_data.get(
            "recommendations",
            []
        )

        if not isinstance(recommendations, list):
            recommendations = []

        state["recommended_providers"] = recommendations

        # --------------------------------------
        # No Providers
        # --------------------------------------

        if len(recommendations) == 0:

            service = requirements.get(
                "service",
                "service"
            )

            location = requirements.get(
                "location",
                ""
            )

            message = (
                f"😔 Sorry, I couldn't find any "
                f"{service} providers"
            )

            if location:
                message += f" in {location}"

            message += (
                ".\n\nPlease try another location."
            )

            return respond(message)

        # --------------------------------------
        # Provider List
        # --------------------------------------

        service = requirements.get(
            "service",
            "service"
        )

        text = (
            f"I found these {service} providers:\n\n"
        )

        for index, item in enumerate(
            recommendations,
            start=1,
        ):

            if not isinstance(item, dict):
                continue

            provider = item.get("provider") or {}

            business = (
                item.get("business_name")
                or item.get("businessName")
                or item.get("provider_name")
                or provider.get("businessName")
                or provider.get("name")
                or "Unknown Provider"
            )

            rating = item.get("rating")

            if isinstance(rating, (int, float)):
                rating = round(rating, 1)
            else:
                rating = "N/A"

            city = (
                item.get("city")
                or provider.get("city")
                or item.get("district")
                or ""
            )

            reason = (
                item.get("reason")
                or item.get("matchReason")
                or ""
            )

            text += (
                f"{index}. {business}\n"
                f"⭐ Rating : {rating}\n"
            )

            if city:
                text += f"📍 {city}\n"

            if reason:
                text += f"💬 {reason}\n"

            text += "\n"

        text += (
            "\nReply with:\n"
        )

        for index in range(
            1,
            len(recommendations) + 1,
        ):
            text += f"\n• Book {index}"

        return respond(text)
        # ==========================================
    # BOOKING FLOW
    # ==========================================

    if action == "book_provider":

        if not booking:

            return respond(
                "❌ I couldn't find the selected provider."
            )

        # Ask booking date
        if not booking.get("date"):

            provider = booking.get(
                "provider_name",
                "the selected provider"
            )

            return respond(
                f"✅ You selected {provider}.\n\n"
                "📅 What date would you like to book?\n\n"
                "Examples:\n"
                "• Tomorrow\n"
                "• Next Monday\n"
                "• 2026-08-25"
            )

        # Ask description
        if not booking.get("description"):

            return respond(
                "📝 Please describe the work you need.\n\n"
                "Examples:\n"
                "• Repair my ceiling fan\n"
                "• Fix my power outlet\n"
                "• Install new lights"
            )

        return respond(
            "✅ I have all the required information.\n"
            "Preparing your booking..."
        )

    # ==========================================
    # CONFIRM BOOKING
    # ==========================================

    if action in (
        "await_confirmation",
        "confirm_booking",
    ):

        provider = booking.get(
            "provider_name",
            "Provider"
        )

        service = booking.get(
            "service",
            "-"
        )

        city = booking.get(
            "city",
            "-"
        )

        date = booking.get(
            "date",
            "-"
        )

        description = booking.get(
            "description",
            "-"
        )

        return respond(
            "📋 Please confirm your booking.\n\n"
            f"👤 Provider : {provider}\n"
            f"🔧 Service : {service}\n"
            f"📍 City : {city}\n"
            f"📅 Date : {date}\n"
            f"📝 Description : {description}\n\n"
            "Reply:\n"
            "• Yes\n"
            "or\n"
            "• No"
        )
        # ==========================================
    # BOOKING STATUS
    # ==========================================

    if action == "booking_status":

        booking_status = state.get("booking_status")

        if isinstance(booking_status, dict):

            booking_info = booking_status.get(
                "booking"
            )

            if isinstance(booking_info, dict):

                return respond(
                    "📋 Booking Details\n\n"
                    f"Booking ID : {booking_info.get('_id', '-')}\n"
                    f"Provider : {booking_info.get('providerName', '-')}\n"
                    f"Service : {booking_info.get('service', '-')}\n"
                    f"City : {booking_info.get('city', '-')}\n"
                    f"Date : {booking_info.get('date', '-')}\n"
                    f"Description : {booking_info.get('description', '-')}\n"
                    f"Status : {booking_info.get('status', 'Pending')}"
                )

            if booking_status.get("message"):

                return respond(
                    booking_status["message"]
                )

        elif isinstance(booking_status, str):

            return respond(
                booking_status
            )

        return respond(
            "I couldn't find your booking."
        )

    # ==========================================
    # ASK MORE INFORMATION
    # ==========================================

    if action == "ask_more_information":

        missing = planner.get(
            "missing_fields",
            []
        )

        if not isinstance(
            missing,
            list,
        ):
            missing = []

        questions = []

        if "service" in missing:

            questions.append(
                "🔧 What service do you need?"
            )

        if "location" in missing:

            questions.append(
                "📍 Which location?"
            )

        if "date" in missing:

            questions.append(
                "📅 What date would you like to book?"
            )

        if "description" in missing:

            questions.append(
                "📝 Please describe the work you need."
            )

        if questions:

            return respond(
                "\n".join(questions)
            )

        return respond(
            "Please provide a little more information."
        )
        # ==========================================
    # GENERAL RESPONSE
    # ==========================================

    general = state.get("general_response")

    if (
        isinstance(general, str)
        and general.strip()
    ):

        return respond(general)

    # ==========================================
    # BOOKING CREATED FLAG
    # ==========================================

    if state.get("booking_created"):

        booking = state.get("created_booking", {})

        return respond(
            "✅ Booking Created Successfully!\n\n"
            f"Booking ID : {booking.get('_id', '-')}\n"
            f"Provider : {booking.get('providerName', '-')}\n"
            f"Service : {booking.get('serviceName', '-')}\n"
            f"City : {booking.get('city', '-')}\n"
            f"Date : {booking.get('date', '-')}\n"
            f"Description : {booking.get('description', '-')}\n"
            f"Status : {booking.get('status', 'Pending')}"
        )

    # ==========================================
    # DEFAULT RESPONSE
    # ==========================================

    return respond(
        "❓ I didn't understand your request.\n\n"
        "You can say:\n\n"
        "• I need an electrician in Matara\n"
        "• I need a plumber in Galle\n"
        "• Book 1\n"
        "• Tomorrow\n"
        "• Repair my ceiling fan\n"
        "• Yes\n"
        "• Booking status"
    )