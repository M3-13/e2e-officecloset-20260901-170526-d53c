"""Tests for the wardrobe slice: CRUD, category filter, user isolation, upload
validation (format + 413) and owner-only image serving."""

import pytest
from fastapi import Depends, HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user
from app.database import Base, get_db
from app.main import app
from app.models import User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _create_user(email: str) -> int:
    with TestingSessionLocal() as session:
        user = User(email=email, password_hash="x")
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.id


def _override_get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    raw = request.headers.get("x-test-user-id")
    if not raw:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.id == int(raw)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def _override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _auth(user_id: int) -> dict[str, str]:
    return {"x-test-user-id": str(user_id)}


def _create_item(
    client: TestClient,
    user_id: int,
    name: str = "Abendkleid",
    category: str = "top",
    color: str | None = "Schwarz",
    brand: str | None = "Chanel",
    image: bytes | None = None,
    image_name: str = "dress.png",
):
    data: dict[str, str] = {"name": name, "category": category}
    if color is not None:
        data["color"] = color
    if brand is not None:
        data["brand"] = brand
    files = None
    if image is not None:
        files = {"image": (image_name, image, "image/png")}
    return client.post("/api/wardrobe/items", data=data, files=files, headers=_auth(user_id))


def test_requires_auth(client) -> None:
    assert client.get("/api/wardrobe/items").status_code == 401
    assert (
        client.post("/api/wardrobe/items", data={"name": "x", "category": "top"}).status_code == 401
    )
    assert client.get("/api/wardrobe/items/1").status_code == 401


def test_create_list_get_update_delete(client) -> None:
    user_id = _create_user("crud@example.com")
    headers = _auth(user_id)

    content = b"\x89PNG\r\n\x1a\n" + b"x" * 32
    resp = _create_item(
        client,
        user_id,
        name="Abendkleid",
        category="top",
        color="Schwarz",
        brand="Chanel",
        image=content,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Abendkleid"
    assert body["category"] == "top"
    assert body["color"] == "Schwarz"
    assert body["brand"] == "Chanel"
    assert body["image_url"] and body["image_url"].startswith("/api/images/")
    item_id = body["id"]

    resp = client.get("/api/wardrobe/items", headers=headers)
    assert resp.status_code == 200
    assert [item["id"] for item in resp.json()] == [item_id]

    resp = client.get(f"/api/wardrobe/items/{item_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Abendkleid"

    resp = client.patch(
        f"/api/wardrobe/items/{item_id}",
        data={"name": "Rotes Kleid", "category": "bottom", "color": "Rot"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Rotes Kleid"
    assert resp.json()["category"] == "bottom"
    assert resp.json()["color"] == "Rot"

    resp = client.delete(f"/api/wardrobe/items/{item_id}", headers=headers)
    assert resp.status_code == 204

    assert client.get(f"/api/wardrobe/items/{item_id}", headers=headers).status_code == 404


def test_category_filter(client) -> None:
    user_id = _create_user("filter@example.com")
    headers = _auth(user_id)
    _create_item(client, user_id, name="Shirt", category="top", color=None, brand=None)
    _create_item(client, user_id, name="Hose", category="bottom", color=None, brand=None)
    _create_item(client, user_id, name="Schuhe", category="shoes", color=None, brand=None)

    resp = client.get("/api/wardrobe/items?category=top", headers=headers)
    assert resp.status_code == 200
    assert [item["name"] for item in resp.json()] == ["Shirt"]

    resp = client.get("/api/wardrobe/items", headers=headers)
    assert len(resp.json()) == 3


def test_user_isolation(client) -> None:
    user_a = _create_user("a@example.com")
    user_b = _create_user("b@example.com")

    resp = _create_item(client, user_a, name="A-Kleid")
    assert resp.status_code == 201
    item_id = resp.json()["id"]

    assert client.get(f"/api/wardrobe/items/{item_id}", headers=_auth(user_b)).status_code == 404
    assert (
        client.patch(
            f"/api/wardrobe/items/{item_id}", data={"name": "geklaut"}, headers=_auth(user_b)
        ).status_code
        == 404
    )
    assert client.delete(f"/api/wardrobe/items/{item_id}", headers=_auth(user_b)).status_code == 404

    assert client.get("/api/wardrobe/items", headers=_auth(user_b)).json() == []

    assert client.get(f"/api/wardrobe/items/{item_id}", headers=_auth(user_a)).status_code == 200


def test_upload_invalid_format_returns_400(client) -> None:
    user_id = _create_user("format@example.com")
    resp = _create_item(client, user_id, image=b"GIF89a-not-an-image", image_name="bad.gif")
    assert resp.status_code == 400


def test_upload_too_large_returns_413(client, monkeypatch) -> None:
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    user_id = _create_user("big@example.com")
    big = b"\x89PNG\r\n\x1a\n" + b"0" * (1024 * 1024 + 100)
    resp = _create_item(client, user_id, image=big)
    assert resp.status_code == 413


def test_image_owner_only(client) -> None:
    user_a = _create_user("img-a@example.com")
    user_b = _create_user("img-b@example.com")

    content = b"\x89PNG\r\n\x1a\n" + b"owner" * 20
    resp = _create_item(client, user_a, image=content, image_name="photo.png")
    assert resp.status_code == 201
    image_url = resp.json()["image_url"]
    filename = image_url.rsplit("/", 1)[-1]

    resp = client.get(f"/api/images/{filename}", headers=_auth(user_a))
    assert resp.status_code == 200
    assert resp.content == content

    assert client.get(f"/api/images/{filename}", headers=_auth(user_b)).status_code == 403
    assert client.get(f"/api/images/{filename}").status_code == 401
    assert client.get("/api/images/does-not-exist.png", headers=_auth(user_a)).status_code == 404
