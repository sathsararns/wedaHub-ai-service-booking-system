from experiments.legacy.booking_prompt import booking_prompt
from functools import lru_cache
from app.core.llm import get_llm
from experiments.legacy.booking_request import BookingRequest

# Structured Booking Extraction Agent
@lru_cache(maxsize=1)
def get_booking_agent():
    return booking_prompt | get_llm().with_structured_output(BookingRequest)
