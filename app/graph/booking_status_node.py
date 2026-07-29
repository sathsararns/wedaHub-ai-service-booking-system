from app.agents.booking_status_agent import booking_status_agent


def booking_status_node(state):
    """
    Fetch the latest booking status from backend
    and prepare a response.
    """

    # --------------------------------
    # Call Agent
    # --------------------------------
    state = booking_status_agent(state)

    # --------------------------------
    # Error
    # --------------------------------
    if state.get("booking_status_error"):

        state["response"] = (
            "❌ Unable to retrieve your booking.\n\n"
            f"{state['booking_status_error']}"
        )

        return state

    booking = state.get("booking_status")

    if not booking:

        state["response"] = (
            "❌ No booking found."
        )

        return state

    # --------------------------------
    # Provider Details
    # --------------------------------
    provider = booking.get("providerId")

    provider_name = "Unknown"

    if isinstance(provider, dict):

        provider_name = (
            f"{provider.get('firstName', '')} "
            f"{provider.get('lastName', '')}"
        ).strip()

    # --------------------------------
    # Date
    # --------------------------------
    booking_date = booking.get("date", "")

    if booking_date:
        booking_date = booking_date[:10]

    # --------------------------------
    # Response
    # --------------------------------
    state["response"] = (
        "📅 Booking Status\n\n"
        f"Booking ID : {booking.get('_id')}\n"
        f"Provider : {provider_name}\n"
        f"Service : {booking.get('serviceName')}\n"
        f"Date : {booking_date}\n"
        f"Time : {booking.get('time')}\n"
        f"Status : {booking.get('status')}"
    )

    return state