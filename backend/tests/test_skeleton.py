"""Skeleton tests: app import, health endpoint and the stub wiring.

These assert only what is true on both sides of the feature gap: the app boots,
the health route answers, and the declared routes/helpers are registered with
the agreed paths and signatures. They never assert the temporary 501 answer a
stub returns today, since that must change the moment its owning ticket merges.
"""

import inspect

from fastapi.testclient import TestClient

from app import storage
from app.auth import get_current_user
from app.main import app

EXPECTED_ROUTES = {
    ("/api/health", "GET"),
    ("/api/auth/register", "POST"),
    ("/api/auth/login", "POST"),
    ("/api/auth/me", "GET"),
    ("/api/wardrobe/items", "GET"),
    ("/api/wardrobe/items", "POST"),
    ("/api/wardrobe/items/{id}", "GET"),
    ("/api/wardrobe/items/{id}", "PATCH"),
    ("/api/wardrobe/items/{id}", "DELETE"),
    ("/api/images/{filename}", "GET"),
    ("/api/outfits", "GET"),
    ("/api/outfits", "POST"),
    ("/api/outfits/{id}", "GET"),
    ("/api/outfits/{id}", "PATCH"),
    ("/api/outfits/{id}", "DELETE"),
    ("/api/account/me", "DELETE"),
}


def _registered_routes() -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if methods and path:
            for method in methods:
                result.add((path, method))
    return result


def test_app_imports() -> None:
    assert app is not None


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stub_routes_are_registered() -> None:
    registered = _registered_routes()
    for expected in EXPECTED_ROUTES:
        assert expected in registered, f"route not registered: {expected}"


def test_get_current_user_signature() -> None:
    params = list(inspect.signature(get_current_user).parameters)
    assert params[:2] == ["request", "db"]


def test_storage_signatures() -> None:
    save_params = list(inspect.signature(storage.save_upload).parameters)
    assert save_params[:2] == ["content", "filename"]
    assert "user_id" in inspect.signature(storage.delete_user_files).parameters
    assert "path" in inspect.signature(storage.delete_file).parameters
