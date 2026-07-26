from typing import TypedDict, Optional


class GraphState(TypedDict):

    user_input: str

    requirements: Optional[dict]

    planner: Optional[dict]

    providers: Optional[list]

    recommendations: Optional[dict]

    response: Optional[str]