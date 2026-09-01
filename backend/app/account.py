"""Account router: deletion of the current user's account and its data."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .models import User
from .storage import delete_user_files

router = APIRouter(prefix="/api/account", tags=["account"])


@router.delete("/me", status_code=204)
def delete_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete the current user's account.

    Deleting the user cascades to their clothing items, outfits and outfit
    items (see the ORM relationships). Uploaded image files are removed from
    disk via :func:`storage.delete_user_files`.
    """
    user_id = user.id

    db.delete(user)
    db.commit()

    delete_user_files(user_id)
