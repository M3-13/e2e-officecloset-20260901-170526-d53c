"""Outfits router: create, list, open, edit and delete the user's outfits.

Every outfit is scoped to the authenticated user: list/create are filtered by
``WHERE user_id = current_user.id``, and a foreign outfit id (or a foreign
clothing item id) answers 404 so that ownership is never leaked.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from .auth import get_current_user
from .database import get_db
from .models import ClothingItem, Outfit, OutfitItem, User
from .schemas import Outfit as OutfitSchema

router = APIRouter(prefix="/api", tags=["outfits"])


class OutfitCreate(BaseModel):
    name: str | None = None
    item_ids: list[int] | None = None


class OutfitUpdate(BaseModel):
    name: str | None = None
    item_ids: list[int] | None = None


def _require_name(name: str | None) -> str:
    if name is None or not name.strip():
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein")
    if len(name.strip()) > 120:
        raise HTTPException(status_code=400, detail="Name ist zu lang")
    return name.strip()


def _require_item_ids(item_ids: list[int] | None) -> list[int]:
    if item_ids is None:
        raise HTTPException(status_code=400, detail="item_ids fehlt")
    return item_ids


def _item_to_dict(item: ClothingItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category,
        "color": item.color,
        "brand": item.brand,
        "image_url": item.image_url,
        "created_at": item.created_at,
    }


def _outfit_to_dict(outfit: Outfit) -> dict:
    return {
        "id": outfit.id,
        "name": outfit.name,
        "items": [_item_to_dict(oi.clothing_item) for oi in outfit.items],
    }


def _load_outfit(db: Session, user_id: int, outfit_id: int) -> Outfit:
    outfit = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.id == outfit_id, Outfit.user_id == user_id)
        .first()
    )
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    return outfit


def _resolve_items(db: Session, user_id: int, item_ids: list[int]) -> list[ClothingItem]:
    unique_ids = list(dict.fromkeys(item_ids))
    if not unique_ids:
        return []
    items = (
        db.query(ClothingItem)
        .filter(ClothingItem.id.in_(unique_ids), ClothingItem.user_id == user_id)
        .all()
    )
    if len(items) != len(unique_ids):
        raise HTTPException(
            status_code=404, detail="Ein oder mehrere Kleidungsstücke nicht gefunden"
        )
    by_id = {item.id: item for item in items}
    return [by_id[i] for i in item_ids]


@router.get("/outfits", response_model=list[OutfitSchema])
def list_outfits(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    outfits = (
        db.query(Outfit)
        .options(selectinload(Outfit.items).selectinload(OutfitItem.clothing_item))
        .filter(Outfit.user_id == user.id)
        .order_by(Outfit.id.desc())
        .all()
    )
    return [_outfit_to_dict(o) for o in outfits]


@router.post("/outfits", response_model=OutfitSchema, status_code=201)
def create_outfit(
    payload: OutfitCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    name = _require_name(payload.name)
    item_ids = _require_item_ids(payload.item_ids)
    items = _resolve_items(db, user.id, item_ids)
    outfit = Outfit(name=name, user_id=user.id)
    db.add(outfit)
    db.flush()
    for item in items:
        db.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id))
    db.commit()
    loaded = _load_outfit(db, user.id, outfit.id)
    return _outfit_to_dict(loaded)


@router.get("/outfits/{id}", response_model=OutfitSchema)
def get_outfit(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    outfit = _load_outfit(db, user.id, id)
    return _outfit_to_dict(outfit)


@router.patch("/outfits/{id}", response_model=OutfitSchema)
def update_outfit(
    id: int,
    payload: OutfitUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    outfit = db.query(Outfit).filter(Outfit.id == id, Outfit.user_id == user.id).first()
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")

    if payload.name is not None:
        outfit.name = _require_name(payload.name)
    if payload.item_ids is not None:
        items = _resolve_items(db, user.id, payload.item_ids)
        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit.id).delete()
        db.flush()
        for item in items:
            db.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id))
    db.commit()
    loaded = _load_outfit(db, user.id, outfit.id)
    return _outfit_to_dict(loaded)


@router.delete("/outfits/{id}", status_code=204)
def delete_outfit(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    outfit = db.query(Outfit).filter(Outfit.id == id, Outfit.user_id == user.id).first()
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit.id).delete()
    db.delete(outfit)
    db.commit()
