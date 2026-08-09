from fastapi import APIRouter
from pydantic import BaseModel

from app.graph.workflow import graph

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    customerId: str | None = None


@router.get("/")
async def home():
    return {
        "status": "running"
    }


@router.post("/chat")
async def chat(request: ChatRequest):

    state = {
    "session_id": request.customerId or "guest",
    "customer_id": request.customerId,   # <-- ADD THIS
    "user_input": request.message,

    "requirements": None,
    "planner": None,
    "providers": None,
    "recommendations": None,
    "recommended_providers": None,
    "booking": None,
    "booking_result": None,
    "booking_error": None,
    "response": None,
}

    result = graph.invoke(state)

    return {
        "response": result.get("response"),
        "recommendations": result.get("recommended_providers", []),
        "booking": result.get("booking_result"),
    }