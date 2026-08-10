from typing import Optional
from pydantic import BaseModel


class BookingRequest(BaseModel):
    provider_index: Optional[int] = None
    date: str = ""
    description: str = ""