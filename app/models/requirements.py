from pydantic import BaseModel
from typing import Optional


class Requirement(BaseModel):
    service: str
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None