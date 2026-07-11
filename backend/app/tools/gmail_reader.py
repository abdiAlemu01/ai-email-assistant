# gmail_reader.py
"""Gmail Reader Tool"""

from langchain.tools import tool

from ..services import gmail_reader_service


def read_latest_emails(limit: int = 10):
    """
    Retrieve recent emails from the user's Gmail inbox.

    Use this tool when the user asks:
    - Read my latest emails
    - Show recent emails
    - What emails did I receive?

    Returns email sender, subject, and preview.
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



"""
Gmail Reader Tool

Responsible for retrieving recent emails from Gmail
and returning clean email information for the AI agent.
"""


from langchain.tools import tool

from ..services import gmail_reader_service


def extract_email_headers(headers: list) -> dict:
    """
    Extract important fields from Gmail headers.
    """

    email_data = {
        "sender": "",
        "subject": "",
    }

    for header in headers:
        name = header.get("name")

        if name == "From":
            email_data["sender"] = header.get("value")

        elif name == "Subject":
            email_data["subject"] = header.get("value")

    return email_data



# def read_latest_emails(limit: int = 10):
#     """
#     Retrieve the latest emails from the user's Gmail inbox.

#     Returns:
#         A list of emails containing:
#         - message id
#         - sender
#         - subject
#         - preview snippet

#     This tool is used by the AI agent when the user asks
#     about recent emails.
#     """

#     service = gmail_reader_service.get_gmail_service()


#     # Get recent email IDs
#     response = service.users().messages().list(
#         userId="me",
#         maxResults=limit
#     ).execute()


#     messages = response.get("messages", [])

#     emails = []


#     for message in messages:

#         # Get full email metadata
#         email = service.users().messages().get(
#             userId="me",
#             id=message["id"]
#         ).execute()


#         headers = email["payload"].get("headers", [])


#         email_headers = extract_email_headers(headers)


#         emails.append(
#             {
#                 "id": email["id"],
#                 "sender": email_headers["sender"],
#                 "subject": email_headers["subject"],
#                 "snippet": email.get("snippet", "")
#             }
#         )


#     return emails



# read_latest_emails_tool = tool(read_latest_emails)