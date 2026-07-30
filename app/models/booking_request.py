from pydantic import BaseModel


class BookingRequest(BaseModel):

    provider_index: int

    date: str

    description: str