"""Image serving router: owner-only access to uploaded clothing-item images."""

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .auth import get_current_user
from .config import settings
from .database import get_db
from .models import ClothingItem, User

router = APIRouter(prefix="/api/images", tags=["images"])

MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


@router.get("/{filename}")
def get_image(
    filename: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    if os.path.basename(filename) != filename:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")

    item = (
        db.query(ClothingItem).filter(ClothingItem.image_url == f"/api/images/{filename}").first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf dieses Bild")

    path = os.path.join(settings.upload_dir, str(user.id), filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")

    ext = os.path.splitext(filename)[1].lower()
    return FileResponse(path, media_type=MEDIA_TYPES.get(ext, "application/octet-stream"))
