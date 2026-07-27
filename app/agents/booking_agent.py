from app.prompts.booking_prompt import booking_prompt
from app.core.llm import llm
from app.models.booking_request import BookingRequest

booking_agent = booking_prompt | llm.with_structured_output(BookingRequest)