from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app
from fastapi.testclient import TestClient

def test_user_login():
    with TestClient(app) as client:
        response = client.post(
            "/token", data={"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"