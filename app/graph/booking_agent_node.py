from app.agents.booking_agent import booking_agent


def booking_agent_node(state):

    previous_booking = state.get("booking") or {}
    requirements = state.get("requirements") or {}

    # -----------------------------------------
    # Current message
    # -----------------------------------------

    user_input = state.get("user_input", "")

    result = booking_agent.invoke(
        {
            "input": user_input,
            "current_booking": str(previous_booking),
        }
    )

    booking = result.model_dump()

    print("\n===== BOOKING AGENT OUTPUT =====")
    print(booking)

    # -----------------------------------------
    # Merge with previous booking
    # -----------------------------------------

    merged_booking = previous_booking.copy()

    for key, value in booking.items():
        if value not in (None, "", []):
            merged_booking[key] = value

    booking = merged_booking

    # -----------------------------------------
    # Preserve date from requirements
    # -----------------------------------------

    if not booking.get("date"):
        booking["date"] = requirements.get("date")

    # -----------------------------------------
    # Preserve description from requirements
    # -----------------------------------------

    if not booking.get("description"):
        booking["description"] = requirements.get("description")

    # -----------------------------------------
    # Need provider?
    # -----------------------------------------

    if booking.get("provider_id"):

        state["booking"] = booking

        requirements["date"] = booking.get("date")
        requirements["description"] = booking.get("description")
        state["requirements"] = requirements

        print("\n===== FINAL BOOKING =====")
        print(state["booking"])

        return state

    # -----------------------------------------
    # Resolve provider from Book 1
    # -----------------------------------------

    recommended = state.get("recommended_providers") or []

    provider_index = booking.get("provider_index")

    if provider_index is None:
        state["booking_error"] = "Please select a provider first."
        return state

    if provider_index < 0 or provider_index >= len(recommended):
        state["booking_error"] = "Invalid provider selection."
        return state

    recommendation = recommended[provider_index]

    original_index = recommendation.get("provider_index")

    providers = state.get("providers") or []

    if (
        original_index is None
        or original_index < 0
        or original_index >= len(providers)
    ):
        state["booking_error"] = "Selected provider could not be found."
        return state

    provider = providers[original_index]

    booking["provider_id"] = provider["_id"]
    booking["provider_name"] = (
        f"{provider['firstName']} {provider['lastName']}"
    )

    requirements["date"] = booking.get("date")
    requirements["description"] = booking.get("description")

    state["requirements"] = requirements
    state["booking"] = booking

    print("\n===== FINAL BOOKING =====")
    print(state["booking"])

    return state