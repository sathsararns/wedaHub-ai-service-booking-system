from app.agents.booking_agent import booking_agent


def booking_agent_node(state):

    previous_booking = state.get("booking", {})
    requirements = state.get("requirements", {})

    # -------------------------------------------------
    # Extract booking information from LLM
    # -------------------------------------------------

    booking = booking_agent.invoke(
        {
            "input": state.get("user_input", ""),
            "current_booking": str(previous_booking),
        }
    ).model_dump()

    print("\n===== BOOKING AGENT OUTPUT =====")
    print(booking)

    # -------------------------------------------------
    # Preserve provider
    # -------------------------------------------------

    if booking.get("provider_index") is None:
        booking["provider_index"] = previous_booking.get("provider_index")

    # -------------------------------------------------
    # Preserve date
    # -------------------------------------------------

    if not booking.get("date"):
        booking["date"] = (
            previous_booking.get("date")
            or requirements.get("date")
        )

    # -------------------------------------------------
    # Preserve description
    # -------------------------------------------------

    if not booking.get("description"):
        booking["description"] = (
            previous_booking.get("description")
            or requirements.get("description")
        )

    # -------------------------------------------------
    # Validate provider selection
    # -------------------------------------------------

    recommended = state.get("recommended_providers", [])

    provider_index = booking.get("provider_index")

    if provider_index is None:
        state["booking_error"] = "Please select a provider first."
        return state

    if (
        not isinstance(provider_index, int)
        or provider_index < 0
        or provider_index >= len(recommended)
    ):
        state["booking_error"] = "Invalid provider selection."
        return state

    recommendation = recommended[provider_index]

    original_index = recommendation.get("provider_index")

    providers = state.get("providers", [])

    if (
        original_index is None
        or original_index < 0
        or original_index >= len(providers)
    ):
        state["booking_error"] = "Selected provider could not be found."
        return state

    provider = providers[original_index]

    # -------------------------------------------------
    # Save provider information
    # -------------------------------------------------

    booking["provider_id"] = provider["_id"]

    booking["provider_name"] = (
        f"{provider['firstName']} {provider['lastName']}"
    )

    # -------------------------------------------------
    # Save booking
    # -------------------------------------------------

    state["booking"] = booking

    # -------------------------------------------------
    # Keep requirements updated
    # -------------------------------------------------

    requirements["date"] = booking.get("date")
    requirements["description"] = booking.get("description")

    state["requirements"] = requirements

    print("\n===== FINAL BOOKING STATE =====")
    print(state["booking"])

    return state