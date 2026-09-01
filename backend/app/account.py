"""Account router (stub)."""

from fastapi import APIRouter, Depends, HTTPException

from .auth import get_current_user
from .models import User

router = APIRouter(prefix="/api/account", tags=["account"])


@router.delete("/me", status_code=204)
def delete_account(user: User = Depends(get_current_user)) -> None:
    raise HTTPException(status_code=501, detail="account #2 implements this")
