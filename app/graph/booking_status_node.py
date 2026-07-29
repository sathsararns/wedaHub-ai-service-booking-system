from app.agents.booking_status_agent import (
    booking_status_agent
)


def booking_status_node(state):

    state = booking_status_agent(state)

    if state.get("booking_status_error"):

        state["response"] = (
            "❌ Unable to get booking status.\n\n"
            f"{state['booking_status_error']}"
        )

        return state

    booking = state["booking_status"]

    provider = booking.get("providerId", {})

    provider_name = (
        f"{provider.get('firstName', '')} "
        f"{provider.get('lastName', '')}"
    ).strip()

    state["response"] = (
        "📅 Booking Status\n\n"
        f"Booking ID : {booking['_id']}\n"
        f"Provider : {provider_name}\n"
        f"Service : {booking['serviceName']}\n"
        f"Date : {booking['date'][:10]}\n"
        f"Time : {booking['time']}\n"
        f"Status : {booking['status']}"
    )

    return state