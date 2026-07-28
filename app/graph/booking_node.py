from app.tools.booking_tool import BookingTool


def booking_node(state):

    booking = state["booking"]
    
    # Get recommendations from state
    recommendations = state["recommended_providers"]
    
    # Get provider using provider_index from booking
    provider = recommendations[booking["provider_index"]]
    
    provider_id = provider["provider_id"]

    result = BookingTool.create_booking(

        provider_id=provider_id,

        date=booking["date"],

        time=booking["time"]

    )

    state["booking_result"] = result

    return state