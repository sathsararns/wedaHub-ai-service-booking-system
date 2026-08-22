from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PlannerDecision(BaseModel):
    """
    Structured output returned by the Planner Agent.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    next_action: str = Field(
        ...,
        description=(
            "Next workflow action. "
            "Examples: search_services, book_provider, "
            "create_booking, booking_status, ask_login, "
            "ask_more_information, general_chat"
        ),
    )

    missing_fields: List[str] = Field(
        default_factory=list,
        description="List of missing fields required to continue.",
    )

    message: str = Field(
        default="",
        description="Optional planner message.",
    )