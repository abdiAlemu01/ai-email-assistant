

# tools/gmail_send.py
"""
Gmail Send Tool

This tool provides email sending capability with human-in-the-loop approval.
Emails are submitted for review before being sent.
"""

from langchain.tools import tool
from typing import Optional

from ..services.gmail_send_service import (
    send_email_direct,
    send_draft_by_id,
    get_draft_by_id,
    validate_email_address,
    format_email_for_review
)
from ..services.human_review_service import get_review_service


@tool
def send_email(
    to: str,
    subject: str,
    body: str,
    draft_id: Optional[str] = None,
    skip_review: bool = False
) -> dict:
    """
    Send an email with human-in-the-loop approval (production safe).
    
    This tool creates a review request that must be approved by a human
    before the email is actually sent. This prevents accidental sending.
    
    Use this tool when the user asks to:
    - Send an email
    - Send a draft
    - Send a reply
    - Dispatch an email
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        draft_id: Optional draft ID to send existing draft
        skip_review: INTERNAL USE ONLY - Skip human review (default: False)
        
    Returns:
        Dictionary containing:
        - review_id: ID for approval/rejection
        - status: "pending_review" or "sent"
        - email_preview: Preview of email content
        - approval_required: Whether approval is needed
        
    Examples:
        - "Send an email to john@example.com about the meeting"
        - "Send draft draft_123"
        - "Send the reply I just drafted"
    
    IMPORTANT: For production safety, all emails require human approval
    before being sent. The user must approve via the review endpoint.
    """
    try:
        review_service = get_review_service()
        
        # If sending from draft, get draft details
        if draft_id:
            draft_data = get_draft_by_id(draft_id)
            if not draft_data.get("success"):
                return {
                    "success": False,
                    "error": f"Draft not found: {draft_data.get('error', 'Unknown error')}"
                }
            
            to = draft_data.get("to", to)
            subject = draft_data.get("subject", subject)
            body = draft_data.get("body", body)
        
        # Validate recipient email
        if not validate_email_address(to):
            return {
                "success": False,
                "error": f"Invalid recipient email address: {to}"
            }
        
        # Format email for review
        email_preview = format_email_for_review(to, subject, body)
        
        # Skip review if explicitly requested (internal use only)
        if skip_review:
            result = send_email_direct(to, subject, body)
            return {
                "success": result.get("success"),
                "status": "sent" if result.get("success") else "failed",
                "message_id": result.get("message_id"),
                "error": result.get("error")
            }
        
        # Create review request (normal flow)
        review_id = review_service.create_review_request(
            to=to,
            subject=subject,
            body=body,
            draft_id=draft_id,
            metadata={
                "tool": "send_email",
                "source": "ai_agent"
            }
        )
        
        return {
            "success": True,
            "status": "pending_review",
            "review_id": review_id,
            "email_preview": email_preview,
            "approval_required": True,
            "message": (
                f"📧 Email prepared for review:\n"
                f"To: {to}\n"
                f"Subject: {subject}\n\n"
                f"This email requires human approval before sending.\n"
                f"Review ID: {review_id}\n\n"
                f"To approve: Use the review endpoint or UI to approve this email.\n"
                f"To reject: Use the review endpoint or UI to reject this email."
            )
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to prepare email for sending: {str(e)}"
        }


@tool
def send_draft(draft_id: str, skip_review: bool = False) -> dict:
    """
    Send an existing Gmail draft with human-in-the-loop approval.
    
    Use this tool when the user asks to:
    - Send a specific draft
    - Send draft by ID
    - Dispatch a draft email
    
    Args:
        draft_id: Gmail draft ID to send
        skip_review: INTERNAL USE ONLY - Skip human review (default: False)
        
    Returns:
        Dictionary containing review ID and approval status
        
    Examples:
        - "Send draft abc123"
        - "Send the draft I created"
    """
    try:
        review_service = get_review_service()
        
        # Get draft details
        draft_data = get_draft_by_id(draft_id)
        if not draft_data.get("success"):
            return {
                "success": False,
                "error": f"Draft not found: {draft_data.get('error', 'Unknown error')}"
            }
        
        to = draft_data.get("to", "")
        subject = draft_data.get("subject", "")
        body = draft_data.get("body", "")
        thread_id = draft_data.get("thread_id")
        
        # Format email for review
        email_preview = format_email_for_review(to, subject, body, thread_id)
        
        # Skip review if explicitly requested (internal use only)
        if skip_review:
            result = send_draft_by_id(draft_id)
            return {
                "success": result.get("success"),
                "status": "sent" if result.get("success") else "failed",
                "message_id": result.get("message_id"),
                "error": result.get("error")
            }
        
        # Create review request (normal flow)
        review_id = review_service.create_review_request(
            to=to,
            subject=subject,
            body=body,
            draft_id=draft_id,
            thread_id=thread_id,
            metadata={
                "tool": "send_draft",
                "source": "ai_agent"
            }
        )
        
        return {
            "success": True,
            "status": "pending_review",
            "review_id": review_id,
            "draft_id": draft_id,
            "email_preview": email_preview,
            "approval_required": True,
            "message": (
                f"📧 Draft prepared for review:\n"
                f"Draft ID: {draft_id}\n"
                f"To: {to}\n"
                f"Subject: {subject}\n\n"
                f"This draft requires human approval before sending.\n"
                f"Review ID: {review_id}\n\n"
                f"To approve: Use the review endpoint or UI to approve this draft.\n"
                f"To reject: Use the review endpoint or UI to reject this draft."
            )
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to prepare draft for sending: {str(e)}"
        }


# Export the tools
send_email_tool = send_email
send_draft_tool = send_draft
