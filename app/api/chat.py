from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    customerId: Optional[str] = None


@router.post("/chat")
async def chat_api(request: ChatRequest):

    customer_id = request.customer_id or request.customerId

    result = chat(
        session_id=customer_id or "guest",
        customer_id=customer_id,
        user_input=request.message,
    )

    return {
        "response": result.get("response", ""),
        "recommendations": result.get(
            "recommended_providers",
            [],
        ),
        "booking": result.get("booking_result"),
    }