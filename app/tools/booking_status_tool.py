from app.services.booking_status_service import get_booking_status


def booking_status_tool(state):

    booking_result = state.get("booking_result")

    if booking_result is None:

        state["booking_status_error"] = (
            "No booking found in this conversation."
        )

        return state

    booking = booking_result["booking"]

    booking_id = booking["_id"]

    result = get_booking_status(booking_id)

    if result["success"]:

        state["booking_status"] = result["booking"]

    else:

        state["booking_status_error"] = result["error"]

    return state