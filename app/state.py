from typing import TypedDict, Optional


class GraphState(TypedDict, total=False):

    session_id: str
    customer_id: str        # <-- ADD THIS

    user_input: str

    requirements: Optional[dict]

    planner: Optional[dict]

    providers: Optional[list]

    recommendations: Optional[dict]

    recommended_providers: Optional[list]

    booking: Optional[dict]

    booking_result: Optional[dict]

    booking_error: Optional[str]

    response: Optional[str]