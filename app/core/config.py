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

MONGO_URI = os.getenv("MONGO_URI")

DB_NAME = os.getenv("DB_NAME")

# ==========================
# Express Backend
# ==========================

EXPRESS_API = os.getenv("EXPRESS_API")



