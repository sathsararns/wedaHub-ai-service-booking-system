from typing import Optional
from pydantic import BaseModel


class Requirement(BaseModel):
    service: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None