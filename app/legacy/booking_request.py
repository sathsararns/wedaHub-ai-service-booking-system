from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BookingRequest(BaseModel):
    """
    Structured output returned by the Booking Agent.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    provider_index: Optional[int] = Field(
        default=None,
        description="Zero-based provider index (Book 1 -> 0, Book 2 -> 1, etc.)",
    )

    service: str = Field(
        default="",
        description="Requested service category (e.g. Plumbing, Electrical, AC Repair).",
    )

    city: str = Field(
        default="",
        description="Booking location or city.",
    )

    date: str = Field(
        default="",
        description="Booking date exactly as mentioned by the user.",
    )

    description: str = Field(
        default="",
        description="Description of the work to be done.",
    )