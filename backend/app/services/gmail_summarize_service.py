# tools/gmail_summarize.py

"""
Gmail Email Summarization Service

This service handles the extraction and processing of email content
for AI-powered summarization.
"""

from typing import Dict, Any, Optional
import base64
from .gmail_reader_service import get_gmail_service


def get_email_by_id(email_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single email by its ID from Gmail.
    
    Args:
        email_id: The Gmail message ID
        
    Returns:
        Dict containing email data with full content, or None if not found
    """
    try:
        service = get_gmail_service()
        
        email = service.users().messages().get(
            userId="me",
            id=email_id,
            format="full"
        ).execute()
        
        payload = email["payload"]
        headers = payload.get("headers", [])
        
        # Extract email metadata
        email_data = {
            "id": email_id,
            "subject": "",
            "from": "",
            "to": "",
            "date": "",
            "body": "",
            "labels": email.get("labelIds", []),
        }
        
        # Extract headers
        for header in headers:
            header_name = header.get("name", "").lower()
            header_value = header.get("value", "")
            
            if header_name == "subject":
                email_data["subject"] = header_value
            elif header_name == "from":
                email_data["from"] = header_value
            elif header_name == "to":
                email_data["to"] = header_value
            elif header_name == "date":
                email_data["date"] = header_value
        
        # Extract email body
        email_data["body"] = _extract_email_body(payload)
        
        return email_data
        
    except Exception as e:
        print(f"Error fetching email {email_id}: {str(e)}")
        return None


def _extract_email_body(payload: Dict[str, Any]) -> str:
    """
    Extract the text body from an email payload.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        Extracted email body text
    """
    body = ""
    
    # Check for direct body data
    if "body" in payload and "data" in payload["body"]:
        body = _decode_base64(payload["body"]["data"])
        return body
    
    # Check for multipart message
    if "parts" in payload:
        body = _extract_from_parts(payload["parts"])
    
    return body


def _extract_from_parts(parts: list) -> str:
    """
    Extract text from multipart email message.
    
    Args:
        parts: List of message parts
        
    Returns:
        Combined text content
    """
    text_content = ""
    
    for part in parts:
        mime_type = part.get("mimeType", "")
        
        # Recursively extract from nested parts
        if "parts" in part:
            text_content += _extract_from_parts(part["parts"])
        
        # Extract text/plain content
        elif mime_type == "text/plain" and "data" in part.get("body", {}):
            text_content += _decode_base64(part["body"]["data"])
        
        # Extract text/html as fallback (basic extraction)
        elif mime_type == "text/html" and "data" in part.get("body", {}) and not text_content:
            html_content = _decode_base64(part["body"]["data"])
            # Basic HTML tag removal (can be improved with BeautifulSoup if needed)
            text_content += _strip_html_tags(html_content)
    
    return text_content


def _decode_base64(data: str) -> str:
    """
    Decode base64 encoded email content.
    
    Args:
        data: Base64 encoded string
        
    Returns:
        Decoded UTF-8 string
    """
    try:
        decoded_bytes = base64.urlsafe_b64decode(data)
        return decoded_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error decoding base64: {str(e)}")
        return ""


def _strip_html_tags(html_text: str) -> str:
    """
    Basic HTML tag removal for email content.
    
    Args:
        html_text: HTML content
        
    Returns:
        Plain text with HTML tags removed
    """
    import re
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)
    
    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def prepare_email_for_summarization(email_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Prepare email data for AI summarization by creating a clean, concise format.
    
    Args:
        email_data: Raw email data dictionary
        
    Returns:
        Formatted email data ready for AI processing
    """
    # Truncate body to reasonable length (avoid token overflow)
    body = email_data.get("body", "")
    max_body_length = 3000  # ~750 tokens
    
    if len(body) > max_body_length:
        body = body[:max_body_length] + "..."
    
    return {
        "subject": email_data.get("subject", "No subject"),
        "from": email_data.get("from", "Unknown sender"),
        "to": email_data.get("to", ""),
        "date": email_data.get("date", "Unknown date"),
        "body": body
    }
