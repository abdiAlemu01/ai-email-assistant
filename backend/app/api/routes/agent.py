# agent.py
"""Agent API routes"""

from fastapi import APIRouter
from pydantic import BaseModel

from ...agents.email_agent import create_email_agent, model

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentRequest(BaseModel):
    query: str


@router.post("/run")
async def run_agent(request: AgentRequest):
    """Run the email agent with a natural language query"""
    agent = create_email_agent(model)
    response = agent.invoke({"messages": [("human", request.query)]})
    return {"messages": response["messages"]}
