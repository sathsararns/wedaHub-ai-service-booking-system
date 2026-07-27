from app.tools.booking_tool import BookingTool


def create_booking(
    provider,
    booking,
):

    return BookingTool.create_booking(

        provider["_id"],

        booking.date,

        booking.time,

    )