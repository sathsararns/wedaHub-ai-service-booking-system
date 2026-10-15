"""Request contracts for chat endpoints, including frontend field aliases."""
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    customer_id: str | None = Field(default=None, alias="customerId")
    session_id: str | None = Field(default=None, alias="sessionId")


class ResetRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str | None = Field(default=None, alias="customerId")
    session_id: str | None = Field(default=None, alias="sessionId")
