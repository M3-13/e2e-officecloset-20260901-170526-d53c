"""Skeleton tests: app import, health endpoint and the stub wiring.

These assert only what is true on both sides of the feature gap: the app boots,
the health route answers, and the declared routes/helpers are registered with
the agreed paths and signatures. Route registration is checked against the
OpenAPI schema (not ``app.routes``), because newer FastAPI/Starlette stores
included routers as ``_IncludedRouter`` objects that do not flatten into
``app.routes`` — while the OpenAPI schema always lists the real API surface.
They never assert the temporary 501 answer a stub returns today, since that
must change the moment its owning ticket merges.
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


def test_app_imports() -> None:
    assert app is not None


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stub_routes_are_registered() -> None:
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    for path, method in EXPECTED_ROUTES:
        assert path in paths, f"path not in OpenAPI schema: {path}"
        assert method.lower() in paths[path], f"method not in OpenAPI schema: {method} {path}"


def test_get_current_user_signature() -> None:
    params = list(inspect.signature(get_current_user).parameters)
    assert params[:2] == ["request", "db"]


def test_storage_signatures() -> None:
    save_params = list(inspect.signature(storage.save_upload).parameters)
    assert save_params[:2] == ["content", "filename"]
    assert "user_id" in inspect.signature(storage.delete_user_files).parameters
    assert "path" in inspect.signature(storage.delete_file).parameters
