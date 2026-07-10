# gmail_reader_service.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

def get_gmail_service():

    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service