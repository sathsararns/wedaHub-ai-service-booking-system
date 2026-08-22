import re

from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.planner import PlannerDecision


# ==========================================================
# Planner LLM (Fallback Only)
# ==========================================================

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Planner Agent.

Your ONLY responsibility is deciding the next workflow.

Available actions

1. search_services
2. book_provider
3. await_confirmation
4. create_booking
5. booking_status
6. ask_login
7. ask_more_information
8. general_chat
9. response

Return ONLY structured output.
""",
        ),
        (
            "human",
            """
Current State

{requirements}
""",
        ),
    ]
)

planner_llm = (
    prompt
    | llm.with_structured_output(PlannerDecision)
)


def planner_agent(state: dict):

    user = str(state.get("user_input", "")).strip().lower()

    requirements = state.get("requirements") or {}
    booking = state.get("booking") or {}

    customer_id = state.get("customer_id")

    recommended = state.get("recommended_providers") or []

    print("\n========== PLANNER ==========")
    print("User :", user)
    print("Requirements :", requirements)
    print("Booking :", booking)

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

    try:

        result = planner_llm.invoke(
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

    except Exception as e:

        print("Planner LLM Error:", e)

    # =====================================================
    # Default
    # =====================================================

    return {
        "next_action": "response",
        "missing_fields": [],
        "message": "",
    }