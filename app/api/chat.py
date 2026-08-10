from fastapi import APIRouter
from pydantic import BaseModel, Field, ConfigDict

from app.services.chat_service import chat

router = APIRouter()


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    customerId: str | None = Field(
        default=None,
        alias="customer_id",
    )


@router.post("/chat")
async def chat_api(request: ChatRequest):

    print("\n========== CHAT API ==========")
    print("REQUEST:")
    print(request)

    print("\nMESSAGE:")
    print(request.message)

    print("\nCUSTOMER ID:")
    print(request.customerId)

    result = chat(
        session_id=request.customerId or "guest",
        customer_id=request.customerId,
        user_input=request.message,
    )

    return {
        "response": result.get("response"),
        "recommendations": result.get("recommended_providers", []),
        "booking": result.get("booking_result"),
    }