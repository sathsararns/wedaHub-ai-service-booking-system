"""
Operational endpoints for the semantic provider index — not part of the
chat flow, not bridged through Express, and not called by the frontend.
Useful for a demo ("here's the index status") and for forcing a rebuild
right after bulk provider data changes instead of waiting for the
10-minute TTL in app/rag/provider_index.py to expire on its own.
"""

from fastapi import APIRouter

from app.rag.provider_index import index_status, refresh_index

router = APIRouter(prefix="/rag")


@router.get("/status")
async def rag_status():
    return index_status()


@router.post("/refresh")
async def rag_refresh():
    return refresh_index()
