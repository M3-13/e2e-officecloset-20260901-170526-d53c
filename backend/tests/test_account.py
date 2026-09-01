"""Tests for account deletion.

These tests use an in-memory database and dependency overrides so they never
touch the real ``wardrobe.db`` or the real upload directory. ``get_current_user``
is still owned by the auth ticket, so it is overridden here with a real user.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import get_current_user
from app.database import Base, get_db
from app.main import app
from app.models import ClothingItem, Outfit, OutfitItem, User


@pytest.fixture
def db_session(tmp_path) -> Session:
    # A file-backed database is used because the endpoint runs in a threadpool
    # (FastAPI sync route), so the connection must be usable across threads.
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def _make_user(db: Session, email: str = "anna@example.com") -> User:
    user = User(email=email, password_hash="hash")
    db.add(user)
    db.flush()
    return user


def test_delete_account_removes_user_items_outfits_and_files(
    db_session: Session, tmp_path, monkeypatch
) -> None:
    user = _make_user(db_session)
    user_id = user.id

    item = ClothingItem(
        user_id=user_id,
        name="Blazer",
        category="top",
        image_url="/api/images/abc.png",
    )
    db_session.add(item)
    outfit = Outfit(user_id=user_id, name="Outfit 1")
    db_session.add(outfit)
    db_session.flush()
    db_session.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id))
    db_session.commit()

    upload_dir = tmp_path / "uploads"
    user_dir = upload_dir / str(user_id)
    user_dir.mkdir(parents=True)
    (user_dir / "abc.png").write_bytes(b"image-bytes")

    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))

    def override_get_db() -> Session:
        return db_session

    def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        client = TestClient(app)
        response = client.delete("/api/account/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204

    assert db_session.query(User).filter_by(id=user_id).first() is None
    assert db_session.query(ClothingItem).filter_by(user_id=user_id).count() == 0
    assert db_session.query(Outfit).filter_by(user_id=user_id).count() == 0
    assert db_session.query(OutfitItem).count() == 0
    assert not os.path.exists(user_dir)
