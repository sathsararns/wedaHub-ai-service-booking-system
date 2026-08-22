from typing import TypedDict, Optional


class GraphState(TypedDict, total=False):
    # =====================================================
    # Session
    # =====================================================

    session_id: str
    customer_id: str

    # =====================================================
    # User
    # =====================================================

    user_input: str
    response: str
    general_response: str

    # =====================================================
    # Requirements
    # =====================================================

    requirements: Optional[dict]

    # =====================================================
    # Planner
    # =====================================================

    planner: Optional[dict]

    # =====================================================
    # Search
    # =====================================================

    providers: Optional[list]

    recommendations: Optional[dict]

    recommended_providers: Optional[list]

    # =====================================================
    # Booking
    # =====================================================

    booking: Optional[dict]

    booking_result: Optional[dict]

    booking_status: Optional[object]

    booking_error: Optional[str]

    booking_created: bool

    created_booking: Optional[dict]

    booking_card: Optional[dict]

    # =====================================================
    # Misc
    # =====================================================

    planner_error: Optional[str]