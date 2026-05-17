import os
import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key")
COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "access_token")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app


def ensure_user(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/register", data={"username": username, "password": password}
    )
    if response.status_code not in {200, 400}:
        raise AssertionError("Unexpected response while ensuring test user")


def test_user_login_success_sets_cookie():
    with TestClient(app) as client:
        username = f"user-{uuid4().hex}"
        ensure_user(client, username, "testpassword")
        response = client.post(
            "/login", data={"username": username, "password": "testpassword"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "ok"
        assert f"{COOKIE_NAME}=" in response.headers.get("set-cookie", "")


def test_user_login_invalid_password():
    with TestClient(app) as client:
        username = f"user-{uuid4().hex}"
        ensure_user(client, username, "testpassword")
        response = client.post(
            "/login", data={"username": username, "password": "wrong"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"


def test_read_user_mails_by_category():
    with TestClient(app) as client:
        username = f"user-{uuid4().hex}"
        ensure_user(client, username, "testpassword")
        login_response = client.post(
            "/login", data={"username": username, "password": "testpassword"}
        )
        assert login_response.status_code == 200

        response = client.get("/mails", params={"mail_category": "その他"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        response = client.get("/mails", params={"mail_category": "仕事"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid mail category"


def test_read_user_mails_requires_auth():
    with TestClient(app) as client:
        response = client.get("/mails")
        assert response.status_code == 401


def test_register_user():
    with TestClient(app) as client:
        username = f"user-{uuid4().hex}"
        response = client.post(
            "/register", data={"username": username, "password": "testpassword"}
        )

        assert response.status_code == 200
        assert response.json()["username"] == username

        duplicate_response = client.post(
            "/register", data={"username": username, "password": "testpassword"}
        )
        assert duplicate_response.status_code == 400

