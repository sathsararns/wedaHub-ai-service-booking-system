import re

from app.agents.booking_agent import booking_agent


def is_empty(value):
    """
    Returns True if value is None or empty string.
    """
    return value is None or (
        isinstance(value, str)
        and value.strip() == ""
    )


def fill_booking_defaults(booking, requirements):
    """
    Fill booking fields from requirements if missing.
    """

    mapping = {
        "service": "service",
        "city": "location",
        "date": "date",
        "description": "description",
    }

    for booking_key, requirement_key in mapping.items():

        if is_empty(booking.get(booking_key)):

            booking[booking_key] = (
                requirements.get(requirement_key)
            )

    return booking


def booking_agent_node(state):

    print("\n========== BOOKING AGENT NODE ==========")
    print(state)

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not state.get("customer_id"):

        state["planner"] = {
            "next_action": "ask_login"
        }

        state["response"] = (
            "🔒 Please log in to create a booking."
        )

        return state

    # =====================================================
    # LOAD STATE
    # =====================================================

    previous_booking = (
        state.get("booking") or {}
    )

    requirements = (
        state.get("requirements") or {}
    )

    user_input = (
        state.get("user_input", "")
    )

    print("\nPrevious Booking")
    print(previous_booking)

    print("\nRequirements")
    print(requirements)

    print("\nUser Input")
    print(user_input)

    # =====================================================
    # EXTRACT BOOKING DATA USING LLM
    # =====================================================

    extracted = {}

    try:

        result = booking_agent.invoke(
            {
                "input": user_input,
                "current_booking": str(previous_booking),
            }
        )

        if result:

            if hasattr(result, "model_dump"):

                extracted = result.model_dump()

            elif hasattr(result, "dict"):

                extracted = result.dict()

            elif isinstance(result, dict):

                extracted = result

    except Exception as e:

        print("\nBooking Agent Error")
        print(e)

        extracted = {}

    # =====================================================
    # FALLBACK REGEX
    # =====================================================

    if extracted.get("provider_index") is None:

        match = re.search(
            r"\bbook\s*(\d+)\b",
            user_input,
            re.IGNORECASE,
        )

        if match:

            extracted["provider_index"] = (
                int(match.group(1)) - 1
            )

    print("\nBooking Agent Output")
    print(extracted)

    # =====================================================
    # MERGE WITH PREVIOUS BOOKING
    # =====================================================

    booking = previous_booking.copy()

    for key, value in extracted.items():

        if value is None:
            continue

        if isinstance(value, str):

            value = value.strip()

            if not value:
                continue

        booking[key] = value

    booking = fill_booking_defaults(
        booking,
        requirements,
    )

    print("\nMerged Booking")
    print(booking)

    # =====================================================
    # PROVIDER SELECTION
    # =====================================================

    if not booking.get("provider_id"):

        provider_index = booking.get(
            "provider_index"
        )

        if isinstance(provider_index, str):

            if provider_index.isdigit():

                provider_index = int(provider_index)

            else:

                provider_index = None

        elif isinstance(provider_index, float):

            if provider_index.is_integer():

                provider_index = int(provider_index)

            else:

                provider_index = None

        elif isinstance(provider_index, bool):

            provider_index = None

        booking["provider_index"] = provider_index

        if provider_index is None:

            state["booking_error"] = (
                "Please select a provider first."
            )

            return state
                # =====================================================
        # LOAD RECOMMENDED PROVIDERS
        # =====================================================

        recommendations = (
            state.get("recommended_providers") or []
        )

        if not recommendations:

            state["booking_error"] = (
                "No providers available."
            )

            return state

        # =====================================================
        # VALIDATE PROVIDER INDEX
        # =====================================================

        if (
            provider_index < 0
            or provider_index >= len(recommendations)
        ):

            state["booking_error"] = (
                "Invalid provider selection."
            )

            return state

        recommendation = recommendations[
            provider_index
        ]

        if not isinstance(recommendation, dict):

            state["booking_error"] = (
                "Invalid provider data."
            )

            return state

        # =====================================================
        # LOAD ALL PROVIDERS
        # =====================================================

        providers = state.get("providers") or []

        provider = None

        # =====================================================
        # METHOD 1
        # Find using original provider_index
        # =====================================================

        original_index = recommendation.get(
            "provider_index"
        )

        if (
            isinstance(original_index, int)
            and 0 <= original_index < len(providers)
        ):

            provider = providers[
                original_index
            ]

        # =====================================================
        # METHOD 2
        # Find using Provider ID
        # =====================================================

        if provider is None:

            recommendation_id = (
                recommendation.get("_id")
                or recommendation.get("provider_id")
            )

            if recommendation_id:

                provider = next(

                    (
                        item
                        for item in providers
                        if str(
                            item.get("_id")
                        ) == str(recommendation_id)
                    ),

                    None,

                )

        # =====================================================
        # PROVIDER NOT FOUND
        # =====================================================

        if provider is None:

            state["booking_error"] = (
                "Selected provider not found."
            )

            return state

        # =====================================================
        # SAVE PROVIDER INFORMATION
        # =====================================================

        provider_id = str(
            provider.get("_id", "")
        )

        if not provider_id:

            state["booking_error"] = (
                "Provider ID missing."
            )

            return state

        booking["provider_id"] = provider_id

        provider_name = (
            f"{provider.get('firstName', '')} "
            f"{provider.get('lastName', '')}"
        ).strip()

        if not provider_name:

            provider_name = (
                provider.get("businessName")
                or provider.get("name")
                or "Provider"
            )

        booking["provider_name"] = provider_name

        # =====================================================
        # COPY DEFAULT VALUES
        # =====================================================

        booking = fill_booking_defaults(
            booking,
            requirements,
        )

        print("\nSelected Provider")
        print(provider)

        print("\nBooking After Provider Selection")
        print(booking)
            # =====================================================
    # UPDATE REQUIREMENTS
    # =====================================================

    requirements.update({

        "service":
            booking.get("service")
            or requirements.get("service"),

        "location":
            booking.get("city")
            or requirements.get("location"),

        "date":
            booking.get("date")
            or requirements.get("date"),

        "description":
            booking.get("description")
            or requirements.get("description"),

    })

    # =====================================================
    # SAVE STATE
    # =====================================================

    state["booking"] = booking
    state["requirements"] = requirements

    # =====================================================
    # CLEAR OLD ERRORS
    # =====================================================

    state.pop("booking_error", None)

    # =====================================================
    # DEBUG OUTPUT
    # =====================================================

    print("\n========== FINAL BOOKING ==========")
    print(booking)

    print("\n========== UPDATED REQUIREMENTS ==========")
    print(requirements)

    # =====================================================
    # NEXT ACTION
    # =====================================================

    state["planner"] = {
        "next_action": "confirm_booking"
    }

    # =====================================================
    # RETURN
    # =====================================================

    return state