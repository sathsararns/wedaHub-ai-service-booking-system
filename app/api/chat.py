from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    customerId: str | None = None


@router.post("/chat")
async def chat_api(request: ChatRequest):

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