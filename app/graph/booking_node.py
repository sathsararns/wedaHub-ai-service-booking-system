from app.tools.booking_tool import BookingTool


def booking_node(state):

    booking = state.get("booking")

    if not booking:
        state["response"] = "❌ Booking information not found."
        return state

    result = BookingTool.create_booking(
        provider_id=booking["provider_id"],
        service=state["requirements"]["service"],
        date=booking["date"],
        time=booking["time"],
        customer_id=state.get("customer_id"),
    )

    state["booking_result"] = result

    return state