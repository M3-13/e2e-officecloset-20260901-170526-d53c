"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Category = Literal["top", "bottom", "shoes", "accessory"]


class Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Category
    color: str | None = None
    brand: str | None = None
    image_url: str | None = None
    created_at: datetime


class Outfit(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    items: list[Item]


class Register(BaseModel):
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
