

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


def read_latest_emails(limit: int = 5):
    """
    Retrieve recent emails from the user's Gmail inbox.

    Use this tool when the user asks:
    - Read my latest emails
    - Show recent emails
    - What emails did I receive?

    Returns email data in structured format matching the frontend Email interface.
    """

    service = gmail_reader_service.get_gmail_service()

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
            "threadId": email.get("threadId", ""),
            "subject": "",
            "from": "",
            "to": "",
            "date": "",
            "snippet": email.get("snippet", ""),
            "body": "",
            "attachments": [],
            "labels": email.get("labelIds", []),
            "isRead": "UNREAD" not in email.get("labelIds", []),
            "isStarred": "STARRED" in email.get("labelIds", [])
        }

        for header in headers:
            if header["name"] == "Subject":
                email_data["subject"] = header["value"]
            elif header["name"] == "From":
                email_data["from"] = header["value"]
            elif header["name"] == "To":
                email_data["to"] = header["value"]
            elif header["name"] == "Date":
                email_data["date"] = header["value"]

        # Extract body
        email_data["body"] = extract_email_body(payload)
        
        # Extract attachments
        email_data["attachments"] = extract_attachments(payload)

        emails.append(email_data)

    return emails


read_latest_emails_tool = tool(read_latest_emails)
