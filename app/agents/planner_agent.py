from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.planner import PlannerDecision

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Planner Agent.

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

    user = state.get("user_input", "").lower().strip()

    requirements = state.get("requirements") or {}
    booking = state.get("booking") or {}

    # ---------------------------------------
    # Booking already started
    # ---------------------------------------

    if booking.get("provider_id"):
        return {
            "next_action": "book_provider",
            "missing_fields": None,
            "message": "Continue booking.",
        }

    # ---------------------------------------
    # Booking Status
    # ---------------------------------------

    if (
        "booking status" in user
        or user == "status"
        or "check booking" in user
        or "show booking" in user
        or "my booking" in user
    ):
        return {
            "next_action": "booking_status",
            "missing_fields": None,
            "message": "Checking booking status.",
        }

    # ---------------------------------------
    # User selected provider
    # ---------------------------------------

    if user.startswith("book"):
        return {
            "next_action": "book_provider",
            "missing_fields": None,
            "message": "Booking selected provider.",
        }

    # ---------------------------------------
    # Search
    # ---------------------------------------

    if (
        requirements.get("service")
        and requirements.get("location")
    ):
        return {
            "next_action": "search_services",
            "missing_fields": None,
            "message": "Searching providers.",
        }

    # ---------------------------------------
    # Missing Information
    # ---------------------------------------

    missing = []

    if not requirements.get("service"):
        missing.append("service")

    if not requirements.get("location"):
        missing.append("location")

    if missing:
        return {
            "next_action": "ask_more_information",
            "missing_fields": missing,
            "message": "Need more information.",
        }

    # ---------------------------------------
    # LLM Fallback
    # ---------------------------------------

    result = planner_llm.invoke(
        {
            "requirements": str(requirements)
        }
    )

    return result.model_dump()