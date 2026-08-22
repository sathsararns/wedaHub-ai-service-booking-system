from langchain_groq import ChatGroq

from app.core.config import GROQ_API_KEY, MODEL_NAME

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=0.3,
)