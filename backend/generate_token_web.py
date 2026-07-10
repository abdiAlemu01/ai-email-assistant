import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from google_auth_oauthlib.flow import Flow
from fastapi import FastAPI, Request
import uvicorn
import threading
import webbrowser
import os

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

CLIENT_SECRETS_FILE = "credentials.json"
REDIRECT_PATH = "/oauth2callback"
HOST = "127.0.0.1"
PORT = 8000

if not os.path.exists(CLIENT_SECRETS_FILE):
    raise SystemExit(f"Missing {CLIENT_SECRETS_FILE}. Download it from Google Cloud Console and place it in this folder.")

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=f"http://{HOST}:{PORT}{REDIRECT_PATH}",
)

app = FastAPI()


@app.get(REDIRECT_PATH)
async def oauth2callback(request: Request):
    """Handle OAuth2 callback and save token.json"""
    # Full redirect including code and state
    authorization_response = str(request.url)
    # Exchange code for tokens
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials

    with open("token.json", "w") as f:
        f.write(creds.to_json())

    # Stop the server after a short delay to allow response to be sent
    def _stop_server():
        try:
            server.should_exit = True
        except Exception:
            pass

    threading.Timer(1.0, _stop_server).start()
    return "<html><body><h2>Authentication complete</h2><p>You can close this window.</p></body></html>"


def run_server():
    global server
    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    auth_url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    print("Opening browser to:", auth_url)
    webbrowser.open(auth_url, new=1)
    run_server()





