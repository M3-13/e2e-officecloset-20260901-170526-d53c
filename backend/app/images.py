"""Image serving router (stub)."""

from fastapi import APIRouter, Depends, HTTPException

from .auth import get_current_user
from .models import User

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/{filename}")
def get_image(filename: str, user: User = Depends(get_current_user)) -> bytes:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")
