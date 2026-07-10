# agent.py
"""Agent API routes"""

from fastapi import APIRouter

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/run")
async def run_agent(payload: dict):
    """Placeholder endpoint to trigger an agent flow"""
    return {"message": "agent run invoked", "payload": payload}
