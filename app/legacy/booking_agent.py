from app.legacy.booking_prompt import booking_prompt
from app.core.llm import llm
from app.legacy.booking_request import BookingRequest

# Structured Booking Extraction Agent
booking_agent = (
    booking_prompt
    | llm.with_structured_output(
        BookingRequest
    )
)