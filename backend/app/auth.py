"""Authentication router (stub) and the shared ``get_current_user`` dependency."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import Login, Register, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    raise HTTPException(status_code=501, detail="auth #7 implements this")


@router.post("/register", response_model=Token)
def register(payload: Register) -> Token:
    raise HTTPException(status_code=501, detail="auth #7 implements this")


@router.post("/login", response_model=Token)
def login(payload: Login) -> Token:
    raise HTTPException(status_code=501, detail="auth #7 implements this")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    raise HTTPException(status_code=501, detail="auth #7 implements this")
