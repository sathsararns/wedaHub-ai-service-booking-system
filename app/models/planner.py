from pydantic import BaseModel
from typing import List, Optional


class PlannerDecision(BaseModel):
    next_action: str
    missing_fields: Optional[List[str]] = None
    message: Optional[str] = None