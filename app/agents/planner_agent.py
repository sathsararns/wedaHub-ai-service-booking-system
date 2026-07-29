from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.models.planner import PlannerDecision


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the Planner Agent.

Your job is to decide the next step.

Available actions:

1. search_services
- User wants to search providers.

2. book_provider
- User says:
Book 1
Book 2
Book Kasun
Book Piyal

3. booking_status
- User asks:
What's my booking status?
Booking status
Status
Check booking
Show booking details

4. ask_more_information
- Service missing
- Location missing

Return structured output only.
"""
        ),
        ("human", "{requirements}")
    ]
)

planner_llm = prompt | llm.with_structured_output(
    PlannerDecision
)


def planner_agent(state: dict):

    user = state["user_input"].lower().strip()

    # -------------------------
    # Booking Status
    # -------------------------

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
            "message": "Checking booking status."
        }

    # -------------------------
    # Booking
    # -------------------------

    if user.startswith("book"):

        return {
            "next_action": "book_provider",
            "missing_fields": None,
            "message": "Booking selected provider."
        }

    # -------------------------
    # Search
    # -------------------------

    result = planner_llm.invoke(
        {
            "requirements": str(
                state.get("requirements", {})
            )
        }
    )

    return result.model_dump()