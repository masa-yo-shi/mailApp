import os
import base64
import sqlite3
from email.utils import parsedate_to_datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, "mail.sqlite")

# These files are intentionally NOT committed for public releases.
# Provide them locally to use Gmail sync.
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

def auth_gmail():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=2000)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_header(headers, name):
    for h in headers:
        if h["name"] == name:
            return h["value"]
    return None

def decode_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            body = decode_body(part)
            if body:
                return body
    data= payload.get("body", {}).get("data")
    if not data:
        return None
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

def main():
    service = auth_gmail()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    results = service.users().messages().list(
        userId="me",
        maxResults=10
    ).execute()

    messages = results.get("messages", [])
    inserted_count = 0
    skipped_count = 0

    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        payload = detail.get("payload", {})
        headers = payload.get("headers", [])

        subject = get_header(headers, "Subject") or "(no subject)"
        date_str = get_header(headers, "Date")
        body = decode_body(payload) or ""

        if not date_str:
            continue

        created_at = parsedate_to_datetime(date_str).isoformat()
        exists = cur.execute(
            "SELECT 1 FROM mails WHERE title = ? AND created_at = ? LIMIT 1",
            (subject, created_at),
        ).fetchone()
        if exists:
            skipped_count += 1
            continue

        cur.execute(
            "INSERT INTO mails (title, description, created_at, category) VALUES (?, ?, ?, ?)",
            (subject, body, created_at, "inbox")
        )
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Mails synced. inserted={inserted_count}, skipped={skipped_count}")
    
if __name__ == "__main__":
        main()



