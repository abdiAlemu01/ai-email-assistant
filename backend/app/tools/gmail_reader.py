

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
                attachments.append(part.get("filename"))
            if "parts" in part:
                attachments.extend(extract_attachments(part))
    
    return attachments


def format_email(email_data):
    """Format email data into the desired structure."""
    formatted = f"""Subject:
{email_data.get('subject', 'No Subject')}

From:
{email_data.get('from', 'Unknown')}

To:
{email_data.get('to', 'Unknown')}

Date:
{email_data.get('date', 'Unknown')}

Body:
{email_data.get('body', 'No body content')}

Attachments:
{', '.join(email_data.get('attachments', [])) if email_data.get('attachments') else 'None'}"""
    return formatted


def read_latest_emails(limit: int = 5):
    """
    Retrieve recent emails from the user's Gmail inbox.

    Use this tool when the user asks:
    - Read my latest emails
    - Show recent emails
    - What emails did I receive?

    Returns email data in structured format with subject, from, to, date, body, and attachments.
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
            "subject": "",
            "from": "",
            "to": "",
            "date": "",
            "body": "",
            "attachments": []
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

        # Format the email
        formatted_email = format_email(email_data)
        emails.append(formatted_email)

    return emails


read_latest_emails_tool = tool(read_latest_emails)
