"""Tests for the outfits router: CRUD, user isolation and foreign-item 404s.

The auth layer is still being implemented by another ticket, so these tests
override ``get_current_user`` with a stub that returns a fixed user and override
``get_db`` with a session bound to an isolated in-memory database. They assert
the behaviour this ticket owns: outfits are scoped to their owner and foreign
outfit/item ids answer 404.
"""

from collections.abc import Iterator
from contextlib import suppress

import pytest
from fastapi import Depends, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user
from app.database import Base, get_db
from app.main import app
from app.models import ClothingItem, Outfit, OutfitItem, User


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    def override_current_user(request: Request, db=Depends(get_db)) -> User:
        return db.query(User).filter(User.id == 1).first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def seed(client: TestClient) -> Iterator[Session]:
    """Open a session on the same engine the app's ``get_db`` override uses."""
    override = app.dependency_overrides[get_db]
    generator = override()
    session = next(generator)
    try:
        yield session
    finally:
        with suppress(StopIteration):
            next(generator)


def _make_user(session: Session, user_id: int, email: str) -> User:
    user = User(id=user_id, email=email, password_hash="x")
    session.add(user)
    session.commit()
    return user


def _make_item(session: Session, user_id: int, name: str, category: str = "top") -> ClothingItem:
    item = ClothingItem(user_id=user_id, name=name, category=category)
    session.add(item)
    session.commit()
    return item


def test_create_and_list_own_outfit(client: TestClient, seed: Session) -> None:
    _make_user(seed, 1, "a@example.com")
    top = _make_item(seed, 1, "Seidenbluse")
    bottom = _make_item(seed, 1, "Anzughose", category="bottom")

    response = client.post(
        "/api/outfits",
        json={"name": "Red Carpet", "item_ids": [top.id, bottom.id]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Red Carpet"
    assert {i["id"] for i in body["items"]} == {top.id, bottom.id}

    listing = client.get("/api/outfits")
    assert listing.status_code == 200
    assert [o["name"] for o in listing.json()] == ["Red Carpet"]


def test_create_requires_nonempty_name(client: TestClient, seed: Session) -> None:
    _make_user(seed, 1, "a@example.com")

    empty = client.post("/api/outfits", json={"name": "", "item_ids": []})
    assert empty.status_code == 400
    assert isinstance(empty.json()["detail"], str)

    missing = client.post("/api/outfits", json={"item_ids": []})
    assert missing.status_code == 400
    assert isinstance(missing.json()["detail"], str)

    assert client.post("/api/outfits", json={"name": "X", "item_ids": []}).status_code == 201


def test_get_update_delete_own_outfit(client: TestClient, seed: Session) -> None:
    _make_user(seed, 1, "a@example.com")
    top = _make_item(seed, 1, "Bluse")
    shoes = _make_item(seed, 1, "Pumps", category="shoes")

    created = client.post("/api/outfits", json={"name": "Gala", "item_ids": [top.id]}).json()
    outfit_id = created["id"]

    fetched = client.get(f"/api/outfits/{outfit_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Gala"

    updated = client.patch(
        f"/api/outfits/{outfit_id}",
        json={"name": "Gala Deluxe", "item_ids": [top.id, shoes.id]},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Gala Deluxe"
    assert {i["id"] for i in updated.json()["items"]} == {top.id, shoes.id}

    empty_rename = client.patch(f"/api/outfits/{outfit_id}", json={"name": "   "})
    assert empty_rename.status_code == 400
    assert isinstance(empty_rename.json()["detail"], str)

    assert client.delete(f"/api/outfits/{outfit_id}").status_code == 204
    assert client.get(f"/api/outfits/{outfit_id}").status_code == 404


def test_user_isolation_on_outfits(client: TestClient, seed: Session) -> None:
    _make_user(seed, 1, "a@example.com")
    _make_user(seed, 2, "b@example.com")
    top_a = _make_item(seed, 1, "Bluse A")
    _make_item(seed, 2, "Bluse B")

    created = client.post(
        "/api/outfits", json={"name": "Mein Outfit", "item_ids": [top_a.id]}
    ).json()

    other = Outfit(name="Fremdes Outfit", user_id=2)
    seed.add(other)
    seed.commit()
    seed.add(OutfitItem(outfit_id=other.id, clothing_item_id=top_a.id))
    seed.commit()

    listing = client.get("/api/outfits").json()
    assert [o["id"] for o in listing] == [created["id"]]
    assert client.get(f"/api/outfits/{other.id}").status_code == 404
    assert client.patch(f"/api/outfits/{other.id}", json={"name": "X"}).status_code == 404
    assert client.delete(f"/api/outfits/{other.id}").status_code == 404


def test_foreign_item_ids_return_404(client: TestClient, seed: Session) -> None:
    _make_user(seed, 1, "a@example.com")
    _make_user(seed, 2, "b@example.com")
    foreign = _make_item(seed, 2, "Fremde Bluse")

    assert (
        client.post("/api/outfits", json={"name": "X", "item_ids": [foreign.id]}).status_code == 404
    )

    own = _make_item(seed, 1, "Eigene Bluse")
    created = client.post("/api/outfits", json={"name": "Y", "item_ids": [own.id]}).json()
    assert (
        client.patch(f"/api/outfits/{created['id']}", json={"item_ids": [foreign.id]}).status_code
        == 404
    )


def test_nonexistent_outfit_returns_404(client: TestClient, seed: Session) -> None:
    _make_user(seed, 1, "a@example.com")

    assert client.get("/api/outfits/9999").status_code == 404
    assert client.patch("/api/outfits/9999", json={"name": "X"}).status_code == 404
    assert client.delete("/api/outfits/9999").status_code == 404
