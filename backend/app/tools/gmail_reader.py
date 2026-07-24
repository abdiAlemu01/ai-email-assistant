

from typing import Union
from langchain.tools import tool
import base64

from ..services import gmail_reader_service


def extract_email_body(payload):
    """Extract the email body from Gmail payload."""
    body = ""
    
    if "parts" in payload:
        # Multipart message
        for part in payload["parts"]:
            if "parts" in part:
                # Nested multipart
                body += extract_email_body(part)
            elif "body" in part and "data" in part["body"]:
                body += base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
    elif "body" in payload and "data" in payload["body"]:
        # Single part message
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    
    return body


def extract_attachments(payload):
    """Extract attachment information from Gmail payload."""
    attachments = []
    
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("filename"):
                attachments.append({
                    "filename": part.get("filename"),
                    "mimeType": part.get("mimeType", "application/octet-stream"),
                    "size": part.get("body", {}).get("size")
                })
            if "parts" in part:
                attachments.extend(extract_attachments(part))
    
    return attachments


def read_emails(limit: Union[str, int] = 1):
    """
    Read emails from the user's Gmail inbox and return concise summaries.

    Use this tool whenever the user wants to read, view, check, or inspect emails.

    Typical user requests include:
    - Read my emails
    - Read my latest email
    - Read my newest email
    - Show my recent emails
    - Show the first email
    - Show the first 2 emails
    - Show the first 5 emails
    - Read my last 3 emails
    - What emails did I receive today?
    - Show emails from LinkedIn
    - Read emails from Udemy
    - Show emails from GitHub
    - Read emails from Google
    - Show emails from Amazon
    - Read emails from Abdi
    - Show emails from a specific sender
    - Check my inbox
    - What new emails do I have?

    The tool can retrieve:
    - The latest N emails (up to 5)
    - Emails from a specific sender or organization
    - Concise email summaries including:
        - Sender
        - Subject
        - Date
        - Read/Unread status
        - Snippet
        - Truncated email body
        - Attachment names (if any)

    Args:
        limit (int):
            Number of emails to retrieve.
            Default: 1
            Maximum: 5

        sender (str | None):
            Optional sender name or email address used to filter emails.
            Examples:
            "LinkedIn"
            "Udemy"
            "GitHub"
            "Google"
            "Amazon"
            "abdi@example.com"

    Returns:
        A list of concise email summaries optimized for AI processing while minimizing token usage.
    """

    # Handle string input from LLM
    if isinstance(limit, str):
        limit = int(limit)

    service = gmail_reader_service.get_gmail_service()

    # Cap limit at 5 to avoid token overflow
    limit = min(limit, 5)

    result = service.users().messages().list(
        userId="me",
        maxResults=limit
    ).execute()

    messages = result.get("messages", [])
    emails = []

    for message in messages:
        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = email["payload"]
        headers = payload.get("headers", [])

        email_data = {
            "id": message["id"],
            "subject": "",
            "from": "",
            "date": "",
            "snippet": email.get("snippet", "")[:150],  # Truncate snippet to 150 chars
            "has_attachments": False,
            "attachment_count": 0,
            "is_read": "UNREAD" not in email.get("labelIds", []),
            "is_starred": "STARRED" in email.get("labelIds", [])
        }

        for header in headers:
            if header["name"] == "Subject":
                email_data["subject"] = header["value"]
            elif header["name"] == "From":
                email_data["from"] = header["value"]
            elif header["name"] == "Date":
                email_data["date"] = header["value"]

        # Get attachment info (count only, not full data)
        attachments = extract_attachments(payload)
        email_data["has_attachments"] = len(attachments) > 0
        email_data["attachment_count"] = len(attachments)
        if attachments:
            email_data["attachment_names"] = [att["filename"] for att in attachments[:3]]  # Max 3 names

        emails.append(email_data)

    return {
        "count": len(emails),
        "emails": emails,
        "note": "Email bodies omitted to conserve tokens. Snippets provided instead."
    }


read_emails_tool = tool(read_emails)







# add system prompt for my AI Agent, add memory for the effecience,add stream make response smooth
# add middlewares