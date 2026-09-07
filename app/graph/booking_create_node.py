from __future__ import annotations

from copy import deepcopy

from app.tools.booking_tool import BookingTool


def _clean_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value


def _extract_booking_data(result: dict) -> dict:
    if not isinstance(result, dict):
        return {}

    booking = result.get("booking")
    if isinstance(booking, dict) and booking:
        return booking

    if any(k in result for k in ["_id", "bookingId", "providerId", "provider_id"]):
        return result

    return {}


def booking_create_node(state):
    print("\n========== BOOKING CREATE NODE ==========")
    print(state)

    booking = deepcopy(state.get("booking") or {})
    customer_id = state.get("customer_id")
    auth_token = state.get("auth_token")

    required_fields = ["provider_id", "service", "city", "date", "description"]
    missing = [
        field
        for field in required_fields
        if not _clean_text(booking.get(field))
    ]

    if missing:
        state["booking_status"] = "failed"
        state["booking_error"] = f"Missing booking fields: {', '.join(missing)}"
        state["response"] = "Please complete your booking details first."
        state["planner"] = {"next_action": "response"}
        return state

    try:
        result = BookingTool.create_booking(
            provider_id=booking["provider_id"],
            customer_id=customer_id,
            service=booking["service"],
            city=booking["city"],
            date=booking["date"],
            description=booking["description"],
            auth_token=auth_token,
        )

        if not isinstance(result, dict):
            result = {}

        created_booking = _extract_booking_data(result)

        booking_id = (
            created_booking.get("_id")
            or created_booking.get("bookingId")
            or created_booking.get("id")
            or created_booking.get("booking_id")
            or result.get("bookingId")
            or result.get("booking_id")
        )

        status = (
            created_booking.get("status")
            or result.get("status")
            or "Pending"
        )

        final_booking = {
            "provider_index": booking.get("provider_index"),
            "provider_id": booking.get("provider_id"),
            "provider_name": booking.get("provider_name"),
            "service": _clean_text(booking.get("service")),
            "city": _clean_text(booking.get("city")),
            "date": _clean_text(booking.get("date")),
            "description": _clean_text(booking.get("description")),
            "booking_id": booking_id,
            "status": status,
        }

        final_booking["providerName"] = final_booking["provider_name"]
        final_booking["serviceName"] = final_booking["service"]
        final_booking["bookingId"] = booking_id
        final_booking["bookingStatus"] = status

        state["booking_result"] = final_booking
        state["booking"] = final_booking
        state["booking_status"] = "success"
        state.pop("booking_error", None)
        state["booking_created"] = True

        # Keep booking ID in state if needed later, but DO NOT show it in chat text
        state["created_booking"] = final_booking
        state["booking_card"] = final_booking

        lines = [
            "✅ Booking Created Successfully!",
            "",
            f"Provider : {final_booking.get('provider_name', 'Provider')}",
            f"Service : {final_booking.get('service', '')}",
            f"City : {final_booking.get('city', '')}",
            f"Date : {final_booking.get('date', '')}",
            f"Description : {final_booking.get('description', '')}",
            f"Status : {final_booking.get('status', 'Pending')}",
        ]

        state["response"] = "\n".join(lines)
        state["planner"] = {"next_action": "finish"}

        print("\n========== FINAL BOOKING ==========")
        print(state["booking"])
        return state

    except Exception as e:
        state["booking_status"] = "failed"
        state["booking_error"] = str(e)
        state["response"] = f"❌ Booking Failed\n\n{e}"
        state["booking_created"] = False
        state["planner"] = {"next_action": "response"}
        return state