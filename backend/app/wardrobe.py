"""Wardrobe router: CRUD for the current user's clothing items.

Every query is scoped to the authenticated user (``WHERE user_id =
current_user.id``) so a foreign resource id answers 404, never someone else's
data. Image uploads are validated by extension (JPG/PNG/WebP) and size; the
``Content-Length`` header is checked *before* the request body is read so an
over-limit request answers 413 without buffering the body.
"""

import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.datastructures import FormData, UploadFile

from . import storage
from .auth import get_current_user
from .config import settings
from .database import get_db
from .models import ClothingItem, User
from .schemas import Item

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

CATEGORIES = {"top", "bottom", "shoes", "accessory"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _max_upload_bytes() -> int:
    return settings.max_upload_mb * 1024 * 1024


def _check_content_length(request: Request) -> None:
    """Reject an over-limit request before its body is read (AC-13)."""
    header = request.headers.get("content-length")
    if not header:
        return
    try:
        length = int(header)
    except ValueError:
        return
    if length > _max_upload_bytes():
        raise HTTPException(
            status_code=413,
            detail=f"Anfrage überschreitet die maximale Größe von {settings.max_upload_mb} MB",
        )


def _text(form: FormData, key: str) -> str | None:
    """Return a stripped text-field value, or None when the field is absent."""
    value = form.get(key)
    if isinstance(value, str):
        return value.strip()
    return None


def _upload(form: FormData) -> UploadFile | None:
    value = form.get("image")
    if isinstance(value, UploadFile):
        return value
    return None


async def _read_image(upload: UploadFile) -> tuple[bytes, str]:
    """Validate and read an uploaded image, enforcing extension and size."""
    filename = upload.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Nur JPG-, PNG- und WebP-Dateien sind erlaubt")
    content = await upload.read()
    if len(content) > _max_upload_bytes():
        raise HTTPException(
            status_code=413,
            detail=f"Bild überschreitet die maximale Größe von {settings.max_upload_mb} MB",
        )
    return content, ext


def _image_url(path: str) -> str:
    return f"/api/images/{os.path.basename(path)}"


def _item_path(item: ClothingItem) -> str | None:
    if not item.image_url:
        return None
    filename = item.image_url.rsplit("/", 1)[-1]
    return os.path.join(settings.upload_dir, str(item.user_id), filename)


@router.get("/items", response_model=list[Item])
def list_items(
    category: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Item]:
    query = db.query(ClothingItem).filter(ClothingItem.user_id == user.id)
    if category is not None:
        query = query.filter(ClothingItem.category == category)
    return query.order_by(ClothingItem.created_at.desc(), ClothingItem.id.desc()).all()


@router.post("/items", response_model=Item, status_code=201)
async def create_item(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Item:
    _check_content_length(request)
    form = await request.form()

    name = _text(form, "name")
    category = _text(form, "category")
    color = _text(form, "color")
    brand = _text(form, "brand")
    image = _upload(form)

    if not name:
        raise HTTPException(status_code=400, detail="Name ist erforderlich")
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Ungültige Kategorie")

    item = ClothingItem(
        user_id=user.id,
        name=name,
        category=category,
        color=color or None,
        brand=brand or None,
    )
    if image is not None:
        content, ext = await _read_image(image)
        path = storage.save_upload(content, image.filename or f"image{ext}", user_id=user.id)
        item.image_url = _image_url(path)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/items/{id}", response_model=Item)
def get_item(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Item:
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == id, ClothingItem.user_id == user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
    return item


@router.patch("/items/{id}", response_model=Item)
async def update_item(
    id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Item:
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == id, ClothingItem.user_id == user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")

    _check_content_length(request)
    form = await request.form()

    name = _text(form, "name")
    category = _text(form, "category")
    color = _text(form, "color")
    brand = _text(form, "brand")
    image = _upload(form)

    if name is not None:
        if not name:
            raise HTTPException(status_code=400, detail="Name darf nicht leer sein")
        item.name = name
    if category is not None:
        if category not in CATEGORIES:
            raise HTTPException(status_code=400, detail="Ungültige Kategorie")
        item.category = category
    if color is not None:
        item.color = color or None
    if brand is not None:
        item.brand = brand or None

    old_path: str | None = None
    if image is not None:
        content, ext = await _read_image(image)
        path = storage.save_upload(content, image.filename or f"image{ext}", user_id=user.id)
        old_path = _item_path(item)
        item.image_url = _image_url(path)

    db.commit()
    db.refresh(item)

    if old_path:
        storage.delete_file(old_path)
    return item


@router.delete("/items/{id}", status_code=204)
def delete_item(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    item = (
        db.query(ClothingItem)
        .filter(ClothingItem.id == id, ClothingItem.user_id == user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")

    old_path = _item_path(item)
    db.delete(item)
    db.commit()
    if old_path:
        storage.delete_file(old_path)
