from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.planner import PlannerDecision


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Planner Agent.

Your ONLY responsibility is deciding which workflow to execute.

Return ONLY structured output.

Available actions:

1. search_services
2. book_provider
3. booking_status
4. ask_more_information
""",
        ),
        ("human", "{requirements}"),
    ]
)

planner_llm = prompt | llm.with_structured_output(PlannerDecision)


def planner_agent(state: dict):
    """
    Planner decides ONLY which workflow should run.

    It DOES NOT collect booking details like:
    - date
    - description

    Those are handled by:
        booking_agent_node
        booking_node
    """

    user = state.get("user_input", "").lower().strip()

    requirements = state.get("requirements") or {}
    booking = state.get("booking") or {}

    # =====================================================
    # Existing booking flow
    # =====================================================

    if booking.get("provider_id"):
        return {
            "next_action": "book_provider",
            "missing_fields": [],
            "message": "Continue booking flow.",
        }

    # =====================================================
    # Booking status
    # =====================================================

    booking_status_keywords = [
        "booking status",
        "status",
        "check booking",
        "show booking",
        "my booking",
    ]

    if any(keyword in user for keyword in booking_status_keywords):
        return {
            "next_action": "booking_status",
            "missing_fields": [],
            "message": "Checking booking status.",
        }

    # =====================================================
    # User selected a provider
    # Example:
    # Book 1
    # Book 2
    # =====================================================

    if user.startswith("book"):
        return {
            "next_action": "book_provider",
            "missing_fields": [],
            "message": "Starting booking flow.",
        }

    # =====================================================
    # Search Providers
    # =====================================================

    if requirements.get("service") and requirements.get("location"):
        return {
            "next_action": "search_services",
            "missing_fields": [],
            "message": "Searching providers.",
        }

    # =====================================================
    # Missing Search Requirements
    # Only ask for search-related fields.
    # Booking fields are NOT handled here.
    # =====================================================

    missing = []

    if not requirements.get("service"):
        missing.append("service")

    if not requirements.get("location"):
        missing.append("location")

    if missing:
        return {
            "next_action": "ask_more_information",
            "missing_fields": missing,
            "message": "Need more search information.",
        }

    # =====================================================
    # LLM Fallback
    # =====================================================

    result = planner_llm.invoke(
        {
            "requirements": str(requirements),
        }
    )

    if hasattr(result, "model_dump"):
        return result.model_dump()

    return result