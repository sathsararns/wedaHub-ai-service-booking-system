from functools import lru_cache

import logging
import re

from app.prompts.planner_prompt import planner_prompt

from app.core.llm import get_llm
from app.models.planner import PlannerDecision

logger = logging.getLogger(__name__)


# ==========================================================
# Planner LLM (Fallback Only)
# ==========================================================


@lru_cache(maxsize=1)
def get_planner_llm():
    return planner_prompt | get_llm().with_structured_output(PlannerDecision)


def planner_agent(state: dict):

    user = str(state.get("user_input", "")).strip().lower()

    requirements = state.get("requirements") or {}
    booking = state.get("booking") or {}

    customer_id = state.get("customer_id")

    recommended = state.get("recommended_providers") or []

    session_id = state.get("session_id")

    if state.get("service_change"):
        missing = [field for field in ("service", "location") if not requirements.get(field)]
        return {
            "next_action": "ask_more_information" if missing else "search_services",
            "missing_fields": missing,
            "message": "",
        }

    logger.debug(
        "session=%s user=%r requirements=%s booking=%s",
        session_id,
        user,
        requirements,
        booking,
    )

    # =====================================================
    # Greeting
    # =====================================================

    if user in {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiya",
        "good morning",
        "good afternoon",
        "good evening",
    }:
        return {
            "next_action": "general_chat",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Thanks
    # =====================================================

    if user in {
        "thanks",
        "thank you",
        "thankyou",
        "thx",
    }:
        return {
            "next_action": "general_chat",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Booking Status
    # =====================================================

    booking_status_keywords = [
        "booking status",
        "status",
        "check booking",
        "show booking",
        "track booking",
        "my booking",
        "booking details",
    ]

    if any(k in user for k in booking_status_keywords):
        return {
            "next_action": "booking_status",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Book Provider
    # =====================================================

    if re.search(r"\bbook\s+\d+\b", user, re.IGNORECASE):

        if not customer_id:
            return {
                "next_action": "ask_login",
                "missing_fields": [],
                "message": "",
            }

        return {
            "next_action": "book_provider",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Confirmation
    # =====================================================

    confirmation_words = {
        "yes",
        "y",
        "ok",
        "okay",
        "confirm",
        "confirmed",
        "book it",
        "go ahead",
        "continue",
        "proceed",
        "sure",
    }

    if (
        user in confirmation_words
        or re.search(
            r"\b(yes|confirm|book it|go ahead|continue|proceed|sure)\b",
            user,
            re.IGNORECASE,
        )
    ):

        missing = []

        if not booking.get("provider_id"):
            missing.append("provider")

        if not booking.get("service"):
            missing.append("service")

        if not (booking.get("city") or requirements.get("location")):
            missing.append("location")

        if not booking.get("date"):
            missing.append("date")

        if not booking.get("description"):
            missing.append("description")

        if missing:
            return {
                "next_action": "ask_more_information",
                "missing_fields": missing,
                "message": "",
            }

        return {
            "next_action": "create_booking",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Existing Booking
    # =====================================================

    if booking.get("provider_id"):

        missing = []

        if not booking.get("service"):
            missing.append("service")

        if not (booking.get("city") or requirements.get("location")):
            missing.append("location")

        if not booking.get("date"):
            missing.append("date")

        if not booking.get("description"):
            missing.append("description")

        if missing:
            return {
                "next_action": "book_provider",
                "missing_fields": missing,
                "message": "",
            }

        return {
            "next_action": "await_confirmation",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Search Providers
    # =====================================================

    service = requirements.get("service")
    location = requirements.get("location")

    if service and location and not recommended:
        return {
            "next_action": "search_services",
            "missing_fields": [],
            "message": "",
        }

    # =====================================================
    # Missing Information
    # =====================================================

    missing = []

    if not service:
        missing.append("service")

    if not location:
        missing.append("location")

    if missing:
        service_keywords = [
            "need",
            "looking",
            "want",
            "repair",
            "fix",
            "electrician",
            "plumber",
            "carpenter",
            "cleaner",
            "painter",
            "technician",
            "mason",
            "driver",
        ]

        if any(word in user for word in service_keywords):
            return {
                "next_action": "ask_more_information",
                "missing_fields": missing,
                "message": "",
            }

    # =====================================================
    # LLM Fallback
    # =====================================================

    logger.info(
        "session=%s no deterministic rule matched, falling back to LLM",
        session_id,
    )

    try:

        result = get_planner_llm().invoke(
            {
                "requirements": str(
                    {
                        "user": user,
                        "requirements": requirements,
                        "booking": booking,
                    }
                )
            }
        )

        if hasattr(result, "model_dump"):
            return result.model_dump()

        if hasattr(result, "dict"):
            return result.dict()

        return result

    except Exception:

        logger.exception("session=%s planner LLM fallback failed", session_id)

    # =====================================================
    # Default
    # =====================================================

    return {
        "next_action": "response",
        "missing_fields": [],
        "message": "",
    }
