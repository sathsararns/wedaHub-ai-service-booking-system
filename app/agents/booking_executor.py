from app.tools.booking_tool import BookingTool


def booking_executor(requirements, provider):

    booking = {

        "providerId": provider["_id"],

        "service": requirements["service"],

        "date": requirements["date"],

        "time": requirements["time"]

    }

    return BookingTool.create_booking(
        booking
    )