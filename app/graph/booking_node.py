from traceback import print_exc

from app.tools.booking_tool import BookingTool


def is_empty(value):
    return (
        value is None
        or (
            isinstance(value, str)
            and value.strip() == ""
        )
    )


def booking_node(state):
    """
    Booking Node

    Responsible ONLY for creating the booking after all
    required information has been collected.
    """

    print("\n========== BOOKING NODE ==========")
    print(state)

    customer_id = state.get("customer_id")

    requirements = state.get("requirements") or {}
    booking = state.get("booking") or {}

    # =====================================================
    # LOGIN
    # =====================================================

    if is_empty(customer_id):

        state["booking_error"] = (
            "Customer is not logged in."
        )

        return state

    customer_id = str(customer_id)

    # =====================================================
    # PROVIDER
    # =====================================================

    provider_id = booking.get("provider_id")

    if is_empty(provider_id):

        state["booking_error"] = (
            "Provider information is missing."
        )

        return state

    provider_id = str(provider_id)

    provider_name = (
        booking.get("provider_name")
        or "Provider"
    )

    # =====================================================
    # SERVICE
    # =====================================================

    service = (
        booking.get("service")
        or requirements.get("service")
    )

    if is_empty(service):

        state["booking_error"] = (
            "Service is missing."
        )

        return state

    service = service.strip()

    # =====================================================
    # CITY
    # =====================================================

    city = (
        booking.get("city")
        or requirements.get("location")
        or ""
    )

    city = city.strip()

    # =====================================================
    # DATE
    # =====================================================

    date = (
        booking.get("date")
        or requirements.get("date")
    )

    if is_empty(date):

        state["booking_error"] = (
            "Booking date is missing."
        )

        return state

    date = date.strip()

    # =====================================================
    # DESCRIPTION
    # =====================================================

    description = (
        booking.get("description")
        or requirements.get("description")
    )

    if is_empty(description):

        state["booking_error"] = (
            "Booking description is missing."
        )

        return state

    description = description.strip()

    # =====================================================
    # FINAL BOOKING OBJECT
    # =====================================================

    final_booking = {
        **booking,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "service": service,
        "city": city,
        "date": date,
        "description": description,
    }

    state["booking"] = final_booking

    requirements.update(
        {
            "service": service,
            "location": city,
            "date": date,
            "description": description,
        }
    )

    state["requirements"] = requirements

    print("\n========== CREATE BOOKING ==========")

    print("Provider :", provider_id)
    print("Customer :", customer_id)
    print("Service  :", service)
    print("City     :", city)
    print("Date     :", date)
    print("Desc     :", description)

    try:

        result = BookingTool.create_booking(
            provider_id=provider_id,
            customer_id=customer_id,
            service=service,
            city=city,
            date=date,
            description=description,
        )

        print("\n========== BOOKING RESULT ==========")
        print(result)

        if not result:

            state["booking_error"] = (
                "Booking service returned an empty response."
            )

            return state

        state["booking_result"] = result

        state["booking_status"] = "success"

        state.pop("booking_error", None)

        state["response"] = (
            f"✅ Your booking with "
            f"{provider_name} has been created successfully."
        )

        state.pop("booking", None)

        return state

    except Exception as e:

        print_exc()

        state["booking_error"] = str(e)

        state.pop("booking_result", None)

        state.pop("booking_status", None)

        state.pop("response", None)

        return state