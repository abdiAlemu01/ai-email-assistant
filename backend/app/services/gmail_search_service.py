
# gmail_search_service.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_gmail_service():

    script_path = Path(__file__).resolve()
    current_dir = script_path.parent

    backend_dir = None

    for _ in range(5):
        if (current_dir / "token.json").exists():
            backend_dir = current_dir
            break

        current_dir = current_dir.parent


    if backend_dir is None:
        raise FileNotFoundError(
            "Could not find backend directory with token.json"
        )


    token_path = backend_dir / "token.json"


    creds = Credentials.from_authorized_user_file(
        str(token_path),
        SCOPES
    )


    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service



def search_emails(query: str, limit: int = 10):
    """Search emails from Gmail inbox and return structured data matching the reader service format."""
    
    service = get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=limit
    ).execute()

    messages = response.get("messages", [])
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
        from ..services.gmail_reader_service import extract_email_body
        email_data["body"] = extract_email_body(payload)
        
        # Extract attachments
        from ..services.gmail_reader_service import extract_attachments
        email_data["attachments"] = extract_attachments(payload)

        emails.append(email_data)

    return emails