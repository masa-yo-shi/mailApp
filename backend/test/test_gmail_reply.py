import base64
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gmail_connect import build_reply_raw_message, send_reply


def _decode_raw_message(raw: str) -> str:
    padded = raw + "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")


def test_build_reply_raw_message_headers():
    raw = build_reply_raw_message(
        to_address="recipient@example.com",
        subject="Hello",
        body="Thanks for the update.",
        message_id="message-123",
        references=["reference-1"],
        from_address="sender@example.com",
    )

    decoded = _decode_raw_message(raw)

    assert "To: recipient@example.com" in decoded
    assert "From: sender@example.com" in decoded
    assert "Subject: Re: Hello" in decoded
    assert "In-Reply-To: <message-123>" in decoded
    assert "References: <reference-1> <message-123>" in decoded
    assert "Thanks for the update." in decoded


def test_build_reply_raw_message_respects_re_subject_and_message_id():
    raw = build_reply_raw_message(
        to_address="recipient@example.com",
        subject="Re: Status",
        body="Already replied.",
        message_id="<message-123>",
        references=None,
    )

    decoded = _decode_raw_message(raw)

    assert "Subject: Re: Status" in decoded
    assert "In-Reply-To: <message-123>" in decoded
    assert "References: <message-123>" in decoded


def test_build_reply_raw_message_missing_required_fields():
    try:
        build_reply_raw_message(
            to_address=" ",
            subject="Hi",
            body="Hello",
            message_id="message-123",
        )
        assert False, "Expected ValueError for empty to_address"
    except ValueError:
        pass

    try:
        build_reply_raw_message(
            to_address="recipient@example.com",
            subject=" ",
            body="Hello",
            message_id="message-123",
        )
        assert False, "Expected ValueError for empty subject"
    except ValueError:
        pass

    try:
        build_reply_raw_message(
            to_address="recipient@example.com",
            subject="Hi",
            body=" ",
            message_id="message-123",
        )
        assert False, "Expected ValueError for empty body"
    except ValueError:
        pass

    try:
        build_reply_raw_message(
            to_address="recipient@example.com",
            subject="Hi",
            body=None,
            message_id="message-123",
        )
        assert False, "Expected ValueError for non-string body"
    except ValueError:
        pass

    try:
        build_reply_raw_message(
            to_address="recipient@example.com\ncc: evil@example.com",
            subject="Hi",
            body="Hello",
            message_id="message-123",
        )
        assert False, "Expected ValueError for header injection"
    except ValueError:
        pass

    try:
        build_reply_raw_message(
            to_address="recipient@example.com",
            subject="Hi",
            body="Hello",
            message_id="message-123",
            references="not-a-list",
        )
        assert False, "Expected ValueError for invalid references"
    except ValueError:
        pass


def test_send_reply_calls_service_with_thread_id():
    class FakeSend:
        def __init__(self, user_id: str, body: dict):
            self.user_id = user_id
            self.body = body
            self.executed = False

        def execute(self) -> dict:
            self.executed = True
            return {"id": "sent-1"}

    class FakeMessages:
        def __init__(self):
            self.last_user_id = None
            self.last_body = None
            self.sender = None

        def send(self, userId: str, body: dict):
            self.last_user_id = userId
            self.last_body = body
            self.sender = FakeSend(userId, body)
            return self.sender

    class FakeUsers:
        def __init__(self):
            self.messages_api = FakeMessages()

        def messages(self):
            return self.messages_api

    class FakeService:
        def __init__(self):
            self.users_api = FakeUsers()

        def users(self):
            return self.users_api

    service = FakeService()
    response = send_reply(
        service,
        thread_id="thread-123",
        to_address="recipient@example.com",
        subject="Hello",
        body="Thanks.",
        message_id="message-123",
    )

    assert response["id"] == "sent-1"
    assert service.users_api.messages_api.last_user_id == "me"
    assert service.users_api.messages_api.last_body["threadId"] == "thread-123"
    assert "raw" in service.users_api.messages_api.last_body


def test_send_reply_raises_runtime_error_on_failure():
    class FakeSend:
        def execute(self) -> dict:
            raise Exception("send failed")

    class FakeMessages:
        def send(self, userId: str, body: dict):
            return FakeSend()

    class FakeUsers:
        def messages(self):
            return FakeMessages()

    class FakeService:
        def users(self):
            return FakeUsers()

    try:
        send_reply(
            FakeService(),
            thread_id="thread-123",
            to_address="recipient@example.com",
            subject="Hello",
            body="Thanks.",
            message_id="message-123",
        )
        assert False, "Expected RuntimeError on send failure"
    except RuntimeError:
        pass


def test_send_reply_requires_thread_id():
    try:
        send_reply(
            object(),
            thread_id=" ",
            to_address="recipient@example.com",
            subject="Hello",
            body="Thanks.",
            message_id="message-123",
        )
        assert False, "Expected ValueError for empty thread_id"
    except ValueError:
        pass
