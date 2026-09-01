"""Outfits router (stub)."""

from fastapi import APIRouter, Depends, HTTPException

from .auth import get_current_user
from .models import User
from .schemas import Outfit

router = APIRouter(prefix="/api", tags=["outfits"])


@router.get("/outfits", response_model=list[Outfit])
def list_outfits(user: User = Depends(get_current_user)) -> list[Outfit]:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.post("/outfits", response_model=Outfit, status_code=201)
def create_outfit(user: User = Depends(get_current_user)) -> Outfit:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.get("/outfits/{id}", response_model=Outfit)
def get_outfit(id: int, user: User = Depends(get_current_user)) -> Outfit:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.patch("/outfits/{id}", response_model=Outfit)
def update_outfit(id: int, user: User = Depends(get_current_user)) -> Outfit:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")


@router.delete("/outfits/{id}", status_code=204)
def delete_outfit(id: int, user: User = Depends(get_current_user)) -> None:
    raise HTTPException(status_code=501, detail="outfits #1 implements this")
