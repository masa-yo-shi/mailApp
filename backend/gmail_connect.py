import os
import base64
import sqlite3
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

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

def _ensure_header_value(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if "\n" in value or "\r" in value:
        raise ValueError(f"{name} must not contain newlines")
    return value

def _normalize_message_id(message_id: str) -> str:
    normalized = _ensure_header_value("message_id", message_id).strip()
    if not normalized:
        raise ValueError("message_id is required")
    if normalized.startswith("<") and normalized.endswith(">"):
        return normalized
    return f"<{normalized}>"

def build_reply_raw_message(
    *,
    to_address: str,
    subject: str,
    body: str,
    message_id: str,
    references: list[str] | None = None,
    from_address: str | None = None,
) -> str:
    trimmed_to = _ensure_header_value("to_address", to_address).strip()
    trimmed_subject = _ensure_header_value("subject", subject).strip()

    if not isinstance(body, str):
        raise ValueError("body must be a string")
    trimmed_body = body.strip()

    if not trimmed_to:
        raise ValueError("to_address is required")
    if not trimmed_subject:
        raise ValueError("subject is required")
    if not trimmed_body:
        raise ValueError("body is required")

    normalized_message_id = _normalize_message_id(message_id)
    normalized_references = []
    if references is not None:
        if not isinstance(references, (list, tuple)):
            raise ValueError("references must be a list of strings")
        normalized_references = [_normalize_message_id(reference) for reference in references]

    if normalized_message_id not in normalized_references:
        normalized_references.append(normalized_message_id)

    reply_subject = trimmed_subject
    if not trimmed_subject.lower().startswith("re:"):
        reply_subject = f"Re: {trimmed_subject}"

    message = EmailMessage()
    message["To"] = trimmed_to
    message["Subject"] = reply_subject
    message["In-Reply-To"] = normalized_message_id
    message["References"] = " ".join(normalized_references)
    if from_address is not None:
        trimmed_from = _ensure_header_value("from_address", from_address).strip()
        if not trimmed_from:
            raise ValueError("from_address must not be empty")
        message["From"] = trimmed_from
    message.set_content(trimmed_body)

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return encoded

def send_reply(
    service,
    *,
    thread_id: str,
    to_address: str,
    subject: str,
    body: str,
    message_id: str,
    references: list[str] | None = None,
    from_address: str | None = None,
    user_id: str = "me",
) -> dict:
    trimmed_thread_id = _ensure_header_value("thread_id", thread_id).strip()
    if not trimmed_thread_id:
        raise ValueError("thread_id is required")

    raw_message = build_reply_raw_message(
        to_address=to_address,
        subject=subject,
        body=body,
        message_id=message_id,
        references=references,
        from_address=from_address,
    )

    message_body = {
        "raw": raw_message,
        "threadId": trimmed_thread_id,
    }

    try:
        return (
            service.users()
            .messages()
            .send(userId=user_id, body=message_body)
            .execute()
        )
    except Exception as exc:  # pragma: no cover - google client errors vary
        raise RuntimeError("Failed to send Gmail reply") from exc

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



