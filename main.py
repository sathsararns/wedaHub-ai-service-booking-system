from fastapi import FastAPI

app = FastAPI(title="WedaHub AI Service")


@app.get("/")
async def home():
    return {
        "status": "running"
    }