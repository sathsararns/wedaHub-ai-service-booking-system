from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="WedaHub AI Service")


class ChatRequest(BaseModel):
    message: str
    customer_id: str | None = None


@app.get("/")
async def home():
    return {
        "status": "running"
    }


@app.post("/chat")
async def chat(request: ChatRequest):

    return {
        "success": True,
        "response": f"You said: {request.message}"
    }