from pydantic import BaseModel
from typing import Optional


class Planner(BaseModel):

    next_action: str

    missing_fields: Optional[list] = None

    message: str