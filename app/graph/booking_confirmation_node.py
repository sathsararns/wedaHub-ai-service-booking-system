import re


def is_empty(value):
    return (
        value is None
        or (
            isinstance(value, str)
            and value.strip() == ""
        )
    )


YES_PATTERN = re.compile(
    r"^(yes|y|ok|okay|sure|confirm|confirmed|book it|go ahead)$",
    re.IGNORECASE,
)

NO_PATTERN = re.compile(
    r"^(no|n|cancel|stop)$",
    re.IGNORECASE,
)


def booking_confirmation_node(state):
    """
    Booking confirmation node.

    If all booking details exist:
        -> Ask user to confirm.

    If user says YES:
        -> booking_confirmed=True

    If user says NO:
        -> cancel booking
    """

    print("\n========== BOOKING CONFIRMATION NODE ==========")
    print(state)

    booking = state.get("booking") or {}

    # ----------------------------------------
    # Validate booking data
    # ----------------------------------------

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

        questions = []

        if "provider" in missing:
            questions.append("• Provider")

        if "service" in missing:
            questions.append("• Service")

        if "date" in missing:
            questions.append("• Date")

        if "description" in missing:
            questions.append("• Description")

        state["response"] = (
            "Please provide:\n\n"
            + "\n".join(questions)
        )

        return state

    # ----------------------------------------
    # Read user response
    # ----------------------------------------

    user = (
        state.get("user_input", "")
        .strip()
    )

    # ----------------------------------------
    # YES
    # ----------------------------------------

    if YES_PATTERN.fullmatch(user):

        state["booking_confirmed"] = True

        print("BOOKING CONFIRMED")

        return state

    # ----------------------------------------
    # NO
    # ----------------------------------------

    if NO_PATTERN.fullmatch(user):

        state["booking_confirmed"] = False

        state["response"] = (
            "❌ Booking cancelled."
        )

        return state

    # ----------------------------------------
    # Ask confirmation
    # ----------------------------------------

    state["booking_confirmed"] = False

    state["response"] = (
        "📋 Please confirm your booking.\n\n"
        f"👤 Provider : {booking.get('provider_name', '-')}\n"
        f"🔧 Service : {booking.get('service', '-')}\n"
        f"📍 City : {booking.get('city', '-')}\n"
        f"📅 Date : {booking.get('date', '-')}\n"
        f"📝 Description : {booking.get('description', '-')}\n\n"
        "Reply:\n"
        "• Yes\n"
        "• No"
    )

    return state