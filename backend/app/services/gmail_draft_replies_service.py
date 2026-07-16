"""
Gmail Draft Reply Service

This service handles the creation of draft replies in Gmail
and manages email threading and reply metadata.
"""

from typing import Dict, Any, Optional
from .gmail_summarize_service import get_email_by_id
from .gmail_reader_service import get_gmail_service
import base64
from email.mime.text import MIMEText


def get_user_email_address() -> str:
    """
    Get the authenticated user's email address.
    
    Returns:
        User's email address
    """
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("emailAddress", "")
    except Exception as e:
        print(f"Error getting user email: {str(e)}")
        return ""


def extract_sender_name(from_address: str) -> str:
    """
    Extract the sender's name from email address.
    
    Args:
        from_address: Email address with optional name (e.g., "John Doe <john@example.com>")
        
    Returns:
        Sender's first name or full name
    """
    # Extract name from "Name <email>" format
    if "<" in from_address:
        name = from_address.split("<")[0].strip()
        # Remove quotes if present
        name = name.strip('"').strip("'")
    else:
        # Just email address, extract name from email
        name = from_address.split("@")[0]
        name = name.replace(".", " ").replace("_", " ")
    
    # Get first name
    first_name = name.split()[0] if name else "there"
    
    return first_name


def extract_sender_email(from_address: str) -> str:
    """
    Extract the email address from the from field.
    
    Args:
        from_address: Email address with optional name
        
    Returns:
        Clean email address
    """
    if "<" in from_address and ">" in from_address:
        # Extract email from "Name <email>" format
        return from_address.split("<")[1].split(">")[0].strip()
    return from_address.strip()


def create_draft_in_gmail(
    to: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a draft email in Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject (with Re: prefix if reply)
        body: Email body content
        thread_id: Gmail thread ID (for replies)
        in_reply_to: Message-ID being replied to
        references: References header for threading
        
    Returns:
        Dict containing draft ID and success status
    """
    try:
        service = get_gmail_service()
        
        # Create MIME message
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        
        # Add threading headers for replies
        if in_reply_to:
            message["In-Reply-To"] = in_reply_to
        if references:
            message["References"] = references
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Prepare draft body
        draft_body = {
            "message": {
                "raw": raw_message
            }
        }
        
        # Add thread ID if replying
        if thread_id:
            draft_body["message"]["threadId"] = thread_id
        
        # Create draft
        draft = service.users().drafts().create(
            userId="me",
            body=draft_body
        ).execute()
        
        return {
            "success": True,
            "draft_id": draft["id"],
            "message_id": draft["message"]["id"],
            "thread_id": draft["message"].get("threadId", "")
        }
        
    except Exception as e:
        print(f"Error creating draft: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def prepare_reply_metadata(original_email: Dict[str, Any]) -> Dict[str, str]:
    """
    Prepare metadata needed for creating a threaded reply.
    
    Args:
        original_email: Original email data dictionary
        
    Returns:
        Dict with reply metadata (to, subject, thread_id, etc.)
    """
    # Extract sender info
    from_address = original_email.get("from", "")
    sender_email = extract_sender_email(from_address)
    
    # Prepare subject with Re: prefix
    subject = original_email.get("subject", "No Subject")
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    
    # Get thread ID
    thread_id = original_email.get("threadId", "")
    
    # Get Message-ID for threading
    message_id = original_email.get("id", "")
    
    return {
        "to": sender_email,
        "subject": subject,
        "thread_id": thread_id,
        "in_reply_to": f"<{message_id}@mail.gmail.com>",
        "references": f"<{message_id}@mail.gmail.com>",
        "sender_name": extract_sender_name(from_address),
        "original_subject": original_email.get("subject", ""),
        "original_date": original_email.get("date", "")
    }


def format_reply_body(content: str, user_name: str = "User") -> str:
    """
    Format the reply body with proper signature and spacing.
    
    Args:
        content: Main reply content
        user_name: Name of the user sending the reply
        
    Returns:
        Formatted email body
    """
    # Ensure proper spacing
    formatted = content.strip()
    
    # Add signature if not present
    if not any(sig in formatted.lower() for sig in ["best regards", "sincerely", "thanks,"]):
        formatted += f"\n\nBest regards,\n{user_name}"
    
    return formatted
