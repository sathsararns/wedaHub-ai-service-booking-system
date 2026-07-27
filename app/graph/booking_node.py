from app.services.booking_service import create_booking


def booking_node(state):

    booking = state["booking"]

    provider = state["providers"][booking["provider_index"]]

    booking_data = {

        "providerId": provider["_id"],

        "date": booking["date"],

        "time": booking["time"]

    }

    try:

        result = create_booking(booking_data)

        state["booking_result"] = result

    except Exception as e:

        state["booking_error"] = str(e)

    return state