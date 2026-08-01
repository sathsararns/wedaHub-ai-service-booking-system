from app.tools.booking_tool import BookingTool


def booking_executor(requirements, provider, customer_id=None):

    return BookingTool.create_booking(
        provider["_id"],
        requirements["service"],
        requirements["date"],
        requirements["description"],
        customer_id,
    )