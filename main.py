from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging_config import configure_logging

configure_logging()

from app.api.chat import router as chat_router
from app.api.rag import router as rag_router

app = FastAPI(
    title="WedaHub AI Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(rag_router)

@app.get("/health")
async def health():
    # Liveness only: don't load the embedding model or call Groq for health checks.
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "WedaHub AI Service Running"
    }
