from app.tools.booking_tool import BookingTool


def create_booking(
    provider,
    booking,
):

    return BookingTool.create_booking(

        provider_id=provider["_id"],

        service=provider["category"],

        date=booking.date,

        description=booking.description,

    )