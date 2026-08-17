from traceback import print_exc

from app.tools.booking_tool import BookingTool


def booking_node(state):

    print("\n========== BOOKING NODE ==========")
    print("STATE:")
    print(state)
    print("STATE KEYS:")
    print(list(state.keys()))
    print("CUSTOMER ID:", state.get("customer_id"))

    customer_id = state.get("customer_id")
    requirements = state.get("requirements", {})
    booking = state.get("booking")

    if not booking:
        state["booking_error"] = "Booking information not found."
        return state

    if not customer_id:
        state["booking_error"] = "customer_id is missing."
        return state

    try:

        print("\n===== CREATE BOOKING =====")

        result = BookingTool.create_booking(
            provider_id=booking["provider_id"],
            service=requirements.get("service"),
            date=booking["date"],
            description=booking["description"],
            customer_id=customer_id,
        )

        print(result)

        state["booking_result"] = result

    except Exception as e:

        print_exc()
        state["booking_error"] = str(e)

    return state