# email.py
"""Email API routes"""

from fastapi import APIRouter

from ...tools.gmail_reader import read_latest_emails

router = APIRouter(prefix="/email", tags=["email"])


@router.get("/")
async def list_emails(limit: int = 5):
    """Return latest emails using the gmail reader tool."""
    emails = read_latest_emails(limit)
    return {"count": len(emails), "emails": emails}
