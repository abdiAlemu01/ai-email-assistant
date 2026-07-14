# email.py
"""Email API routes"""

from fastapi import APIRouter, HTTPException
import logging

from ...tools.gmail_reader import read_latest_emails

router = APIRouter(prefix="/email", tags=["email"])
logger = logging.getLogger(__name__)


@router.get("/")
async def list_emails(limit: int = 5):
    """Return latest emails using the gmail reader tool."""
    try:
        logger.info(f"Fetching {limit} emails...")
        emails = read_latest_emails(limit)
        return {"count": len(emails), "emails": emails}
    except ConnectionError as e:
        logger.error(f"Gmail connection error: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="Unable to connect to Gmail. Please check your internet connection and try again."
        )
    except FileNotFoundError as e:
        logger.error(f"Gmail credentials error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Gmail credentials not found. Please ensure credentials.json and token.json exist."
        )
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")
