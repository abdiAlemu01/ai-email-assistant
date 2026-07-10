# gmail_reader.py
"""Gmail Reader Tool"""

from langchain.tools import tool

from ..services import gmail_reader_service


def read_latest_emails(limit: int = 5):
    """
    Read the latest emails from Gmail inbox.
    Returns sender, subject and email content.
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
            id=message["id"]
        ).execute()

        payload = email["payload"]
        headers = payload.get("headers", [])

        subject = ""
        sender = ""

        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]
            if header["name"] == "From":
                sender = header["value"]

        emails.append(
            {
                "sender": sender,
                "subject": subject,
                "snippet": email.get("snippet")
            }
        )

    return emails


read_latest_emails_tool = tool(read_latest_emails)