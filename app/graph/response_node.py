def response_node(state):
    """
    Generate the final response for the user.

    Booking flow:
        1. Login check
        2. Search providers
        3. Select provider
        4. Ask booking date
        5. Ask description
        6. Create booking
        7. Return booking data for frontend

    AI booking does NOT require a time/slot.
    """

    planner = state.get("planner", {})
    action = planner.get("next_action")

    # =====================================================
    # RESET BOOKING CREATED FLAG
    # =====================================================

    state["booking_created"] = False

    # =====================================================
    # SUCCESSFUL BOOKING
    #
    # IMPORTANT:
    # Always check booking_result FIRST.
    # =====================================================

    booking_result = state.get("booking_result")

    if booking_result:

        booking_data = booking_result.get("booking") or {}

        if not isinstance(booking_data, dict):
            booking_data = {}

        # =================================================
        # PROVIDER
        # =================================================

        provider = booking_data.get("providerId") or {}

        provider_name = ""

        if isinstance(provider, dict):

            first_name = provider.get(
                "firstName",
                ""
            )

            last_name = provider.get(
                "lastName",
                ""
            )

            provider_name = (
                f"{first_name} {last_name}"
            ).strip()

        if not provider_name:

            provider_name = (
                booking_data.get(
                    "providerName"
                )
                or state.get(
                    "booking",
                    {}
                ).get(
                    "provider_name",
                    ""
                )
                or "Provider"
            )

        # =================================================
        # BOOKING DATA
        # =================================================

        booking_id = booking_data.get(
            "_id",
            ""
        )

        service_name = (
            booking_data.get(
                "serviceName"
            )
            or booking_data.get(
                "service"
            )
            or state.get(
                "requirements",
                {}
            ).get(
                "service",
                "Service"
            )
        )

        description = (
            booking_data.get(
                "description"
            )
            or state.get(
                "requirements",
                {}
            ).get(
                "description"
            )
            or ""
        )

        date = (
            booking_data.get(
                "date"
            )
            or state.get(
                "requirements",
                {}
            ).get(
                "date"
            )
            or ""
        )

        city = (
            booking_data.get(
                "city"
            )
            or state.get(
                "requirements",
                {}
            ).get(
                "location"
            )
            or ""
        )

        status = (
            booking_data.get(
                "status"
            )
            or "pending"
        )

        # =================================================
        # FORMAT DATE
        # =================================================

        formatted_date = ""

        if date:

            date_string = str(date)

            # MongoDB ISO date
            # 2026-08-14T04:30:00.000Z

            if "T" in date_string:

                formatted_date = (
                    date_string
                    .split("T")[0]
                )

            else:

                formatted_date = date_string

        # =================================================
        # MARK BOOKING AS CREATED
        # =================================================

        state["booking_created"] = True

        # =================================================
        # STORE CLEAN BOOKING OBJECT
        #
        # This is the object the frontend should use.
        # =================================================

        state["created_booking"] = {

            "_id": str(
                booking_id
            ),

            "serviceName": service_name,

            "description": description,

            "date": formatted_date,

            "city": city,

            "status": status,

            "providerName": provider_name,

            "providerId": (
                str(
                    provider.get("_id")
                )
                if isinstance(
                    provider,
                    dict
                )
                and provider.get("_id")
                else ""
            ),

        }

        # =================================================
        # BOOKING CARD DATA
        #
        # IMPORTANT:
        # No price
        # No time
        # No slot
        # No duration
        # No address requirement
        # =================================================

        state["booking_card"] = {

            "_id": str(
                booking_id
            ),

            "serviceName": service_name,

            "description": description,

            "date": formatted_date,

            "city": city,

            "status": status,

            "providerName": provider_name,

            "providerId": (
                str(
                    provider.get("_id")
                )
                if isinstance(
                    provider,
                    dict
                )
                and provider.get("_id")
                else ""
            ),

        }

        # =================================================
        # FINAL TEXT RESPONSE
        # =================================================

        state["response"] = (

            "✅ Booking Created Successfully!\n\n"

            f"Booking ID : "
            f"{booking_id or '-'}\n"

            f"Provider : "
            f"{provider_name}\n"

            f"Service : "
            f"{service_name}\n"

            f"Description : "
            f"{description or '-'}\n"

            f"Date : "
            f"{formatted_date or '-'}\n"

            f"Status : "
            f"{status}"

        )

        return state

    # =====================================================
    # BOOKING ERROR
    # =====================================================

    booking_error = state.get(
        "booking_error"
    )

    if booking_error:

        state["booking_created"] = False

        state["response"] = (

            "❌ Booking Failed!\n\n"

            f"{booking_error}"

        )

        return state

    # =====================================================
    # LOGIN REQUIRED
    # =====================================================

    if action == "ask_login":

        state["response"] = (
            "🔒 Please log in to create a booking."
        )

        return state

    # =====================================================
    # SEARCH RESULT
    # =====================================================

    if action == "search_services":

        recommendation_data = state.get(
            "recommendations",
            {}
        )

        if not isinstance(
            recommendation_data,
            dict
        ):

            recommendation_data = {}

        recommendations = (
            recommendation_data.get(
                "recommendations",
                []
            )
        )

        if not isinstance(
            recommendations,
            list
        ):

            recommendations = []

        state["recommended_providers"] = (
            recommendations
        )

        # -------------------------------------------------
        # NO PROVIDERS
        # -------------------------------------------------

        if not recommendations:

            state["response"] = (

                "No providers found.\n\n"

                "Try changing:\n"

                "- Service\n"
                "- Location"

            )

            return state

        # -------------------------------------------------
        # PROVIDER LIST
        # -------------------------------------------------

        text = (
            "I found these providers for you:\n\n"
        )

        for i, provider in enumerate(
            recommendations,
            start=1
        ):

            if not isinstance(
                provider,
                dict
            ):
                continue

            business_name = (
                provider.get(
                    "business_name"
                )
                or "Unknown"
            )

            reason = (
                provider.get(
                    "reason"
                )
                or ""
            )

            rating = (
                provider.get(
                    "rating"
                )

                if provider.get(
                    "rating"
                ) is not None

                else "N/A"
            )

            text += (

                f"{i}. "
                f"{business_name}\n"

                f"   Reason : "
                f"{reason}\n"

                f"   Rating : "
                f"{rating} ⭐\n\n"

            )

        text += (
            "📅 Reply with:\n\n"
        )

        for i, provider in enumerate(
            recommendations,
            start=1
        ):

            if not isinstance(
                provider,
                dict
            ):
                continue

            business_name = (
                provider.get(
                    "business_name"
                )
                or "Unknown"
            )

            text += (

                f"• Book {i} - "
                f"{business_name}\n"

            )

        text += (
            "\nOr reply with 'More options'."
        )

        state["response"] = text

        return state

    # =====================================================
    # BOOKING FLOW
    # =====================================================

    if action == "book_provider":

        booking = state.get(
            "booking"
        )

        # -------------------------------------------------
        # NO BOOKING DATA
        # -------------------------------------------------

        if not booking:

            state["response"] = (

                "Sorry, I couldn't find "
                "the booking information."

            )

            return state

        if not isinstance(
            booking,
            dict
        ):

            state["response"] = (

                "Sorry, I couldn't process "
                "the booking information."

            )

            return state

        # =================================================
        # DATE
        # =================================================

        date = booking.get(
            "date"
        )

        if not date:

            provider_name = (

                booking.get(
                    "provider_name"
                )

                or "the provider"

            )

            state["response"] = (

                f"📅 You selected "
                f"{provider_name}.\n\n"

                "What date would you like "
                "to book?\n\n"

                "Examples:\n"

                "• Tomorrow\n"
                "• Friday\n"
                "• 15 August"

            )

            return state

        # =================================================
        # DESCRIPTION
        # =================================================

        description = booking.get(
            "description"
        )

        if not description:

            state["response"] = (

                "📝 Please describe the work "
                "you need the provider to do."

            )

            return state

        # =================================================
        # BOOKING DATA READY
        # =================================================

        state["response"] = (

            "Your booking information is ready. "
            "Please wait while I create the booking."

        )

        return state

    # =====================================================
    # BOOKING STATUS
    # =====================================================

    if action == "booking_status":

        booking_status = state.get(
            "booking_status"
        )

        if booking_status:

            state["response"] = (
                booking_status
            )

            return state

        state["response"] = (
            "I couldn't find the booking status."
        )

        return state

    # =====================================================
    # ASK MORE INFORMATION
    # =====================================================

    missing = (
        planner.get(
            "missing_fields"
        )
        or []
    )

    if missing:

        questions = []

        if "service" in missing:

            questions.append(
                "🔧 What service do you need?"
            )

        if "location" in missing:

            questions.append(
                "📍 Which location do you need "
                "the service in?"
            )

        if "date" in missing:

            questions.append(
                "📅 What date would you like "
                "to book?"
            )

        if "description" in missing:

            questions.append(
                "📝 Please describe the work "
                "you need."
            )

        if questions:

            state["response"] = (
                "\n".join(
                    questions
                )
            )

        else:

            state["response"] = (
                "Please provide more information "
                "so I can continue."
            )

        return state

    # =====================================================
    # DEFAULT
    # =====================================================

    state["response"] = (
        "Sorry, I couldn't process your request."
    )

    return state