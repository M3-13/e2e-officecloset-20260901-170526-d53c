"""Authentication tests: register, login, me, wrong password, rate limiting."""

import os

import pytest
from fastapi.testclient import TestClient

from app.auth import rate_limiter
from app.database import SessionLocal
from app.main import app
from app.models import User

os.environ.setdefault(
    "SECRET_KEY", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)


def _clear_users() -> None:
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_state(client: TestClient) -> None:
    _clear_users()
    rate_limiter.reset()
    yield
    rate_limiter.reset()


def _register(client: TestClient, email: str, password: str) -> None:
    response = client.post("/api/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200


def test_register_returns_token(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register", json={"email": "anna@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    _register(client, "dupe@example.com", "secret123")
    response = client.post(
        "/api/auth/register", json={"email": "dupe@example.com", "password": "other456"}
    )
    assert response.status_code == 409
    assert "detail" in response.json()


def test_register_invalid_email_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register", json={"email": "not-an-email", "password": "secret123"}
    )
    assert response.status_code == 422


def test_login_success_returns_token(client: TestClient) -> None:
    _register(client, "ben@example.com", "secret123")
    response = client.post(
        "/api/auth/login", json={"email": "ben@example.com", "password": "secret123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    _register(client, "cara@example.com", "secret123")
    response = client.post(
        "/api/auth/login", json={"email": "cara@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_me_returns_current_user(client: TestClient) -> None:
    _register(client, "dave@example.com", "secret123")
    token = client.post(
        "/api/auth/login", json={"email": "dave@example.com", "password": "secret123"}
    ).json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "dave@example.com"
    assert isinstance(body["id"], int)


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_rate_limit_returns_429(client: TestClient) -> None:
    for _ in range(10):
        response = client.post(
            "/api/auth/login", json={"email": "nobody@example.com", "password": "x"}
        )
        assert response.status_code != 429
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "x"})
    assert response.status_code == 429
    assert "detail" in response.json()
