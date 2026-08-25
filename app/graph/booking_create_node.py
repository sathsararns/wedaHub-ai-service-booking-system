from traceback import print_exc

from app.tools.booking_tool import BookingTool


def booking_create_node(state):
    """
    Booking Create Node
    """

    print("\n========== BOOKING CREATE NODE ==========")
    print(state)

    booking = state.get("booking") or {}
    customer_id = state.get("customer_id")

    # =====================================================
    # VALIDATE
    # =====================================================

    required_fields = [
        "provider_id",
        "service",
        "date",
        "description",
    ]

    missing = []

    for field in required_fields:

        value = booking.get(field)

        if value is None:
            missing.append(field)

        elif isinstance(value, str) and value.strip() == "":
            missing.append(field)

    if missing:

        state["booking_status"] = "failed"

        state["booking_error"] = (
            "Missing booking fields: "
            + ", ".join(missing)
        )

        state["response"] = (
            "Please complete your booking details first."
        )

        state["planner"] = {
            "next_action": "response"
        }

        return state

    # =====================================================
    # CREATE BOOKING
    # =====================================================

    try:

        result = BookingTool.create_booking(
            provider_id=booking["provider_id"],
            customer_id=customer_id,
            service=booking["service"],
            city=booking.get("city", ""),
            date=booking["date"],
            description=booking["description"],
        )

        if not result:
            raise Exception("Booking service returned no response.")

        state["booking_result"] = result
        state["booking_status"] = "success"

        state.pop("booking_error", None)

        # =====================================================
        # BOOKING OBJECT FOR FRONTEND
        # =====================================================

        booking_data = result.get("booking", result)

        state["booking_card"] = booking_data

        state["booking_reference"] = (
            booking_data.get("_id")
            or booking_data.get("bookingId")
            or booking_data.get("id")
            or ""
        )

        # =====================================================
        # TEXT RESPONSE
        # =====================================================

        state["response"] = (
            "✅ Booking Created Successfully!\n\n"
            f"Booking ID : {state['booking_reference']}\n"
            f"Provider : {booking.get('provider_name','Provider')}\n"
            f"Service : {booking.get('service','')}\n"
            f"City : {booking.get('city','')}\n"
            f"Date : {booking.get('date','')}\n"
            f"Description : {booking.get('description','')}\n"
            f"Status : Pending"
        )

        # =====================================================
        # KEEP booking_card
        # =====================================================

        state.pop("booking", None)
        state.pop("requirements", None)
        state.pop("recommended_providers", None)

        state["booking_confirmed"] = False

        state["planner"] = {
            "next_action": "finish"
        }

        return state

    except Exception as e:

        print_exc()

        state["booking_status"] = "failed"

        state["booking_error"] = str(e)

        state["response"] = (
            "❌ Failed to create booking.\n\n"
            f"Reason: {str(e)}"
        )

        state["booking_confirmed"] = False

        state["planner"] = {
            "next_action": "response"
        }

        return state