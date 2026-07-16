"""
Gmail Send Service

This service handles sending emails through Gmail API
with support for drafts, threading, and direct sending.
"""

from typing import Dict, Any, Optional
from .gmail_reader_service import get_gmail_service
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_direct(
    to: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email directly through Gmail API.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        thread_id: Gmail thread ID (for replies)
        in_reply_to: Message-ID being replied to
        references: References header for threading
        
    Returns:
        Dict containing message ID and success status
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
        
        # Prepare send body
        send_body = {
            "raw": raw_message
        }
        
        # Add thread ID if replying
        if thread_id:
            send_body["threadId"] = thread_id
        
        # Send email
        sent_message = service.users().messages().send(
            userId="me",
            body=send_body
        ).execute()
        
        return {
            "success": True,
            "message_id": sent_message["id"],
            "thread_id": sent_message.get("threadId", ""),
            "label_ids": sent_message.get("labelIds", [])
        }
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def send_draft_by_id(draft_id: str) -> Dict[str, Any]:
    """
    Send an existing draft by its draft ID.
    
    Args:
        draft_id: Gmail draft ID to send
        
    Returns:
        Dict containing message ID and success status
    """
    try:
        service = get_gmail_service()
        
        # Send the draft
        sent_message = service.users().drafts().send(
            userId="me",
            body={"id": draft_id}
        ).execute()
        
        return {
            "success": True,
            "message_id": sent_message["id"],
            "thread_id": sent_message.get("threadId", ""),
            "label_ids": sent_message.get("labelIds", [])
        }
        
    except Exception as e:
        print(f"Error sending draft: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_draft_by_id(draft_id: str) -> Dict[str, Any]:
    """
    Retrieve a draft by its ID for review.
    
    Args:
        draft_id: Gmail draft ID
        
    Returns:
        Dict containing draft details
    """
    try:
        service = get_gmail_service()
        
        draft = service.users().drafts().get(
            userId="me",
            id=draft_id,
            format="full"
        ).execute()
        
        message = draft.get("message", {})
        headers = {
            header["name"]: header["value"]
            for header in message.get("payload", {}).get("headers", [])
        }
        
        # Get body
        body = ""
        payload = message.get("payload", {})
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    body_data = part.get("body", {}).get("data", "")
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                        break
        else:
            body_data = payload.get("body", {}).get("data", "")
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")
        
        return {
            "success": True,
            "draft_id": draft_id,
            "message_id": message.get("id", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "body": body,
            "thread_id": message.get("threadId", "")
        }
        
    except Exception as e:
        print(f"Error getting draft: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_draft(draft_id: str) -> Dict[str, Any]:
    """
    Delete a draft by its ID.
    
    Args:
        draft_id: Gmail draft ID to delete
        
    Returns:
        Dict containing success status
    """
    try:
        service = get_gmail_service()
        
        service.users().drafts().delete(
            userId="me",
            id=draft_id
        ).execute()
        
        return {
            "success": True,
            "message": f"Draft {draft_id} deleted successfully"
        }
        
    except Exception as e:
        print(f"Error deleting draft: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def validate_email_address(email: str) -> bool:
    """
    Basic email address validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_email_for_review(
    to: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format email details for human review.
    
    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        thread_id: Optional thread ID
        
    Returns:
        Formatted email details for display
    """
    # Truncate body for preview
    preview = body[:200] + "..." if len(body) > 200 else body
    
    return {
        "to": to,
        "subject": subject,
        "body": body,
        "preview": preview,
        "thread_id": thread_id,
        "is_reply": bool(thread_id),
        "char_count": len(body),
        "word_count": len(body.split())
    }
