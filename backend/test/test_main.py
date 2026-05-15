from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app
from fastapi.testclient import TestClient

def test_user_login():
    with TestClient(app) as client:
        response = client.post(
            "/login", data={"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

def test_read_user_mails_by_category():
    with TestClient(app) as client:
        Login_response = client.post(
            "/login", data={"username": "testuser", "password": "testpassword"}
        )
        accesstoken = Login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {accesstoken}"}
        response = client.get("/mails/その他", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        response = client.get("/mails/仕事", headers=headers)
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid mail category"

