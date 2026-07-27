from app.services.booking_service import create_booking


def booking_node(state):

    booking = state.get("booking")

    if booking is None:
        return state

    provider = state["providers"][booking.provider_index]

    result = create_booking(

        provider,

        booking,

    )

    state["booking_result"] = result

    return state