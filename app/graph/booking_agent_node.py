from app.agents.booking_agent import booking_agent


def booking_agent_node(state):
    """
    Booking agent node.

    Responsibilities:
    - Verify login
    - Parse booking information
    - Merge booking state
    - Resolve selected provider
    """

    print("\n========== BOOKING AGENT NODE ==========")
    print(state)
    print("STATE KEYS:", list(state.keys()))
    print("CUSTOMER ID:", state.get("customer_id"))
    print("SESSION ID:", state.get("session_id"))

    # -------------------------------------------------
    # Login Required
    # -------------------------------------------------

    customer_id = state.get("customer_id")

    if customer_id is None or str(customer_id).strip() == "":
        print("❌ customer_id missing")

        state["planner"] = {
            "next_action": "ask_login"
        }

        state["response"] = "🔒 Please log in to create a booking."

        return state

    print("✅ Logged user:", customer_id)

    previous_booking = state.get("booking", {})
    requirements = state.get("requirements", {})

    # -------------------------------------------------
    # Current message
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Merge booking state
    # -------------------------------------------------

    merged_booking = previous_booking.copy()

    for key, value in booking.items():
        if value not in (None, "", []):
            merged_booking[key] = value

    booking = merged_booking

    # -------------------------------------------------
    # Preserve values from requirements
    # -------------------------------------------------

    if not booking.get("date"):
        booking["date"] = requirements.get("date")

    if not booking.get("description"):
        booking["description"] = requirements.get("description")

    # -------------------------------------------------
    # Provider already resolved
    # -------------------------------------------------

    if booking.get("provider_id"):

        requirements["date"] = booking.get("date")
        requirements["description"] = booking.get("description")

        state["requirements"] = requirements
        state["booking"] = booking

        print("\n===== FINAL BOOKING =====")
        print(state["booking"])

        return state

    # -------------------------------------------------
    # Resolve provider from recommendations
    # -------------------------------------------------

    recommended = state.get("recommended_providers", [])

    provider_index = booking.get("provider_index")

    if provider_index is None:
        state["booking_error"] = "Please select a provider first."
        return state

    if provider_index < 0 or provider_index >= len(recommended):
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