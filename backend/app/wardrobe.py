"""Wardrobe router (stub)."""

from fastapi import APIRouter, Depends, HTTPException

from .auth import get_current_user
from .models import User
from .schemas import Item

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])


@router.get("/items", response_model=list[Item])
def list_items(category: str | None = None, user: User = Depends(get_current_user)) -> list[Item]:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.post("/items", response_model=Item, status_code=201)
def create_item(user: User = Depends(get_current_user)) -> Item:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.get("/items/{id}", response_model=Item)
def get_item(id: int, user: User = Depends(get_current_user)) -> Item:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.patch("/items/{id}", response_model=Item)
def update_item(id: int, user: User = Depends(get_current_user)) -> Item:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")


@router.delete("/items/{id}", status_code=204)
def delete_item(id: int, user: User = Depends(get_current_user)) -> None:
    raise HTTPException(status_code=501, detail="wardrobe #4 implements this")
