# auth.py
"""Authentication API routes"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/health")
async def auth_health():
    return {"status": "ok"}
