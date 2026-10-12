import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Groq
# ==========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "llama-3.1-8b-instant"
)

# ==========================
# MongoDB
# ==========================
# Not currently used by the live chat flow (see experiments/legacy/database.py) —
# kept for whichever future feature ends up needing direct DB access.
# Accepts either MONGO_URI or MONGODB_URI since .env has used both names.

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")

DB_NAME = os.getenv("DB_NAME")

# ==========================
# Express Backend
# ==========================

EXPRESS_API = os.getenv("EXPRESS_API")

# Base URL of the Express backend for endpoints that aren't under
# EXPRESS_API's "/api" prefix pattern (booking creation, booking status).
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")

# ==========================
# Observability (optional)
# ==========================
# LangChain/LangGraph read these directly from the environment — no code
# wiring is required for LangSmith tracing to activate. Exposed here only
# so app/core/logging_config.py can log whether it's turned on.

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "wedahub-ai-service")
