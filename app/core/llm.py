"""Create the shared LLM lazily so imports and offline tests need no API key."""
from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import GROQ_API_KEY, MODEL_NAME


@lru_cache(maxsize=1)
def get_llm():
    return ChatGroq(api_key=GROQ_API_KEY, model=MODEL_NAME, temperature=0.3)
