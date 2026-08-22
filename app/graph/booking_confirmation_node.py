import re


def is_empty(value):
    return (
        value is None
        or (
            isinstance(value, str)
            and value.strip() == ""
        )
    )


def booking_confirmation_node(state):

    print("\n========== BOOKING CONFIRMATION NODE ==========")
    print(state)

    booking = state.get("booking") or {}

    missing = []

    if is_empty(booking.get("provider_id")):
        missing.append("provider")

    if is_empty(booking.get("service")):
        missing.append("service")

    if is_empty(booking.get("date")):
        missing.append("date")

    if is_empty(booking.get("description")):
        missing.append("description")

    if missing:

        state["booking_confirmed"] = False

        state["response"] = (
            "Please provide:\n\n"
            + "\n".join(f"• {m}" for m in missing)
        )

        return state

    user = (
        state.get("user_input", "")
        .strip()
        .lower()
    )

    if re.fullmatch(
        r"(yes|y|ok|okay|confirm|confirmed|sure|book it|go ahead)",
        user,
    ):

        state["booking_confirmed"] = True

        print("BOOKING CONFIRMED")

        return state

    if re.fullmatch(
        r"(no|cancel|stop)",
        user,
    ):

        state["booking_confirmed"] = False

        state["response"] = "Booking cancelled."

        return state

    state["booking_confirmed"] = False

    state["response"] = (
        "📋 Please confirm your booking.\n\n"
        f"👤 Provider : {booking.get('provider_name','-')}\n"
        f"🔧 Service : {booking.get('service','-')}\n"
        f"📍 City : {booking.get('city','-')}\n"
        f"📅 Date : {booking.get('date','-')}\n"
        f"📝 Description : {booking.get('description','-')}\n\n"
        "Reply:\n"
        "• Yes\n"
        "• No"
    )

    return state