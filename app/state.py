from typing import TypedDict, Optional


class GraphState(TypedDict):

    session_id: str

    user_input: str

    requirements: Optional[dict]

    planner: Optional[dict]

    providers: Optional[list]

    recommendations: Optional[dict]

    # <-- මේක GraphState එක ඇතුළේ තියෙන්න ඕනේ
    recommended_providers: Optional[list]

    booking: Optional[dict]

    booking_result: Optional[dict]

    booking_error: Optional[str]

    response: Optional[str]