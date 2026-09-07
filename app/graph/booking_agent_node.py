from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List


BOOK_RE = re.compile(r"\bbook\s*([1-9]\d*)\b", re.IGNORECASE)


def _get_selected_recommendation(state: dict, user_input: str) -> dict | None:
    """
    Returns the selected recommended provider based on 'Book 1', 'Book 2', etc.
    """
    match = BOOK_RE.search(user_input or "")
    if not match:
        return None

    idx = int(match.group(1)) - 1
    recommended = state.get("recommended_providers") or []
    providers = state.get("providers") or []

    if idx < 0 or idx >= len(recommended):
        return None

    rec = recommended[idx]
    original_index = rec.get("provider_index")

    if original_index is None:
        return None

    if original_index < 0 or original_index >= len(providers):
        return None

    provider = providers[original_index]
    return {
        "provider_index": idx,
        "provider_name": rec.get("business_name"),
        "provider_id": provider.get("_id"),
    }


def _normalize_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    return cleaned if cleaned else None


def booking_agent_node(state):
    print("\n========== BOOKING AGENT NODE ==========")
    print(state)

    user_input = (state.get("user_input") or "").strip()
    requirements = deepcopy(state.get("requirements") or {})
    booking = deepcopy(state.get("booking") or {})
    customer_id = state.get("customer_id")

    print("\nPrevious Booking")
    print(booking)

    print("\nRequirements")
    print(requirements)

    # --------------------------------------------------
    # 1) If user chose "Book 1 / Book 2 ..." select provider
    # --------------------------------------------------
    selected = _get_selected_recommendation(state, user_input)
    if selected:
        booking["provider_index"] = selected["provider_index"]
        booking["provider_id"] = selected["provider_id"]
        booking["provider_name"] = selected["provider_name"]

        # Keep service/location already discovered
        if requirements.get("service"):
            booking["service"] = requirements["service"]
        if requirements.get("location"):
            booking["city"] = requirements["location"]

        # We do not want to lose current requirements
        state["booking"] = booking
        state["requirements"] = requirements

        state["planner"] = {
            "next_action": "book_provider",
            "missing_fields": ["date", "description"],
            "message": "",
        }

        state["response"] = (
            f"✅ You selected {booking['provider_name']}.\n\n"
            "📅 What date would you like to book?\n\n"
            "Examples:\n"
            "• Tomorrow\n"
            "• Next Monday\n"
            "• 2026-08-25"
        )

        print("\n========== FINAL BOOKING ==========")
        print(state["booking"])
        print("\n========== BOOKING ROUTER ==========")
        print("Planner :", state["planner"])
        print("Booking :", state["booking"])
        return state

    # --------------------------------------------------
    # 2) If provider already selected, merge date/description into booking
    # --------------------------------------------------
    if booking.get("provider_id"):
        # Sync booking with requirements on every turn
        if requirements.get("service"):
            booking["service"] = requirements["service"]

        if requirements.get("location"):
            booking["city"] = requirements["location"]

        if requirements.get("date"):
            booking["date"] = requirements["date"]

        if requirements.get("description"):
            booking["description"] = requirements["description"]

        # Also keep normalized values on booking itself
        booking["service"] = _normalize_text(booking.get("service"))
        booking["city"] = _normalize_text(booking.get("city"))
        booking["date"] = _normalize_text(booking.get("date"))
        booking["description"] = _normalize_text(booking.get("description"))

        state["booking"] = booking
        state["requirements"] = requirements

        # Decide next response based on what is still missing
        missing: List[str] = []

        if not booking.get("date"):
            missing.append("date")
        if not booking.get("description"):
            missing.append("description")

        if missing == ["date"]:
            state["planner"] = {
                "next_action": "book_provider",
                "missing_fields": ["date"],
                "message": "",
            }
            state["response"] = (
                f"✅ You selected {booking.get('provider_name', 'the provider')}.\n\n"
                "📅 What date would you like to book?\n\n"
                "Examples:\n"
                "• Tomorrow\n"
                "• Next Monday\n"
                "• 2026-08-25"
            )
            print("\nBooking Continues")
            print(state["booking"])
            return state

        if missing == ["description"]:
            state["planner"] = {
                "next_action": "book_provider",
                "missing_fields": ["description"],
                "message": "",
            }
            state["response"] = (
                f"✅ You selected {booking.get('provider_name', 'the provider')}.\n\n"
                f"📅 Date : {booking.get('date')}\n\n"
                "📝 Please describe the work you need."
            )
            print("\nBooking Continues")
            print(state["booking"])
            return state

        if not missing:
            state["planner"] = {
                "next_action": "confirm_booking",
                "missing_fields": [],
                "message": "",
            }
            state["response"] = (
                "📋 Please confirm your booking.\n\n"
                f"👤 Provider : {booking.get('provider_name', '')}\n"
                f"🔧 Service : {booking.get('service', '')}\n"
                f"📍 City : {booking.get('city', '')}\n"
                f"📅 Date : {booking.get('date', '')}\n"
                f"📝 Description : {booking.get('description', '')}\n\n"
                "Reply:\n"
                "• Yes\n"
                "or\n"
                "• No"
            )
            print("\n========== FINAL BOOKING ==========")
            print(state["booking"])
            print("\n========== BOOKING ROUTER ==========")
            print("Planner :", state["planner"])
            print("Booking :", state["booking"])
            return state

        # If only date exists but description missing, ask description
        if booking.get("date") and not booking.get("description"):
            state["planner"] = {
                "next_action": "book_provider",
                "missing_fields": ["description"],
                "message": "",
            }
            state["response"] = (
                f"✅ You selected {booking.get('provider_name', 'the provider')}.\n\n"
                f"📅 Date : {booking.get('date')}\n\n"
                "📝 Please describe the work you need."
            )
            print("\nBooking Continues")
            print(state["booking"])
            return state

    # --------------------------------------------------
    # 3) No provider selected yet, just keep state as-is
    # --------------------------------------------------
    state["booking"] = booking
    state["requirements"] = requirements

    print("\nBooking Continues")
    print(state["booking"])
    return state