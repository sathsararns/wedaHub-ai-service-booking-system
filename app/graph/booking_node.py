from traceback import print_exc

from app.tools.booking_tool import BookingTool


def booking_node(state):

    print("\n========== BOOKING NODE ==========")
    print("STATE:")
    print(state)
    print("STATE KEYS:")
    print(list(state.keys()))

    customer_id = state.get("customer_id")
    print("CUSTOMER ID :", customer_id)

    requirements = state.get("requirements", {})
    print("REQUIREMENTS :", requirements)

    booking = state.get("booking")
    print("BOOKING :", booking)

    if not booking:
        state["response"] = "❌ Booking information not found."
        return state

    if not booking.get("date"):
        state["response"] = "📅 What date would you like to book?"
        return state

    if not customer_id:
        state["booking_error"] = "customer_id is missing."
        state["response"] = "❌ customer_id is missing."
        return state

    try:

        print("\n===== CALLING BOOKING TOOL =====")

        payload = {
            "provider_id": booking["provider_id"],
            "service": requirements.get("service"),
            "date": booking.get("date"),
            "description": booking.get("description"),
            "customer_id": customer_id,
        }

        print(payload)

        result = BookingTool.create_booking(
            provider_id=payload["provider_id"],
            service=payload["service"],
            date=payload["date"],
            description=payload["description"],
            customer_id=payload["customer_id"],
        )

        print("\n===== BOOKING RESULT =====")
        print(result)

        state["booking_result"] = result

        state["response"] = (
            "✅ Booking created successfully!\n\n"
            f"Provider : {booking['provider_name']}\n"
            f"Date : {booking['date']}"
        )

    except Exception as e:

        print("\n===== BOOKING ERROR =====")
        print(type(e).__name__)
        print(e)
        print_exc()

        state["booking_error"] = str(e)
        state["response"] = f"❌ Booking failed.\n\n{e}"

    return state