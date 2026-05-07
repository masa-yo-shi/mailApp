from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_user_login():
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"