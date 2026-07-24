# agent.py
"""Agent API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from ...agents.email_agent import create_email_agent, model

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


class AgentRequest(BaseModel):
    query: str
    thread_id: str = "default"  # Optional thread_id for conversation memory


@router.post("/run")
async def run_agent(request: AgentRequest):
    """Run the email agent with a natural language query"""
    try:
        logger.info(f"Received agent query: {request.query}")
        agent = create_email_agent(model)
        
        # Configuration for memory/checkpointer - thread_id identifies the conversation
        config = {"configurable": {"thread_id": request.thread_id}}
        
        logger.info("Streaming agent response...")
        
        # Stream the agent response and collect messages
        serialized_messages = []
        for event in agent.stream({"messages": [("human", request.query)]}, config):
            logger.info(f"Stream event: {event}")
            
            # Handle different event types from LangGraph streaming
            for key, value in event.items():
                if key == "messages":
                    for msg in value:
                        if hasattr(msg, 'type') and hasattr(msg, 'content'):
                            serialized_messages.append({
                                "type": msg.type,
                                "content": msg.content
                            })
                        elif isinstance(msg, tuple):
                            serialized_messages.append({
                                "type": msg[0],
                                "content": msg[1]
                            })
                        else:
                            logger.warning(f"Unknown message format: {type(msg)}")
                            serialized_messages.append({
                                "type": "unknown",
                                "content": str(msg)
                            })
        
        return {"messages": serialized_messages}
        
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Configuration error: {error_msg}")
        
        # Provide specific error messages for common issues
        if "api_key" in error_msg.lower() or "groq" in error_msg.lower():
            raise HTTPException(
                status_code=500, 
                detail="AI agent configuration error: Groq API key is missing or invalid. Please check your .env file."
            )
        raise HTTPException(status_code=500, detail=f"Agent configuration error: {error_msg}")
        
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="Unable to connect to the AI service. Please check your internet connection."
        )
        
    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
        
        # Try to provide more specific error messages
        error_msg = str(e)
        if "token" in error_msg.lower() or "auth" in error_msg.lower():
            detail = "Authentication error with AI service. Please check your API credentials."
        elif "timeout" in error_msg.lower():
            detail = "AI service request timed out. Please try again."
        elif "rate limit" in error_msg.lower():
            detail = "AI service rate limit exceeded. Please wait and try again."
        else:
            detail = f"Agent execution failed: {error_msg}"
            
        raise HTTPException(status_code=500, detail=detail)
