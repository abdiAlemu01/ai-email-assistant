# gmail_reader_service.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from pathlib import Path


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

def get_gmail_service():
    # Get the backend directory by searching for credentials.json
    # Start from script location and search upward
    script_path = Path(__file__).resolve()
    current_dir = script_path.parent
    
    # Search upward for the backend directory (where credentials.json is located)
    backend_dir = None
    for i in range(5):  # Search up to 5 levels up
        if (current_dir / "credentials.json").exists():
            backend_dir = current_dir
            break
        current_dir = current_dir.parent
    
    if backend_dir is None:
        raise FileNotFoundError(
            "Could not find backend directory with credentials.json. "
            "Please ensure credentials.json is in the backend directory."
        )
    
    token_path = backend_dir / "token.json"
    credentials_path = backend_dir / "credentials.json"
    
    creds = None
    
    # Check if token.json exists
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # If there are no (valid) credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check for credentials.json file
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}. Please download it from Google Cloud Console "
                    "and place it in the backend directory. See README for instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service