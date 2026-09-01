"""Authentication: register, login, token decoding and rate limiting."""

import re
import threading
import time
from collections import defaultdict, deque

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User
from .schemas import Login, Register, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_TOKEN_LIFETIME_SECONDS = 7 * 24 * 60 * 60
_RATE_LIMIT = 10
_RATE_WINDOW_SECONDS = 60.0


class RateLimiter:
    """In-memory sliding-window request counter keyed by client IP."""

    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window_seconds:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


rate_limiter = RateLimiter(limit=_RATE_LIMIT, window_seconds=_RATE_WINDOW_SECONDS)


def _client_ip(request: Request) -> str:
    if request.client is not None:
        return request.client.host
    return "unknown"


def _enforce_rate_limit(request: Request) -> None:
    if not rate_limiter.allow(_client_ip(request)):
        raise HTTPException(
            status_code=429,
            detail="Zu viele Anfragen. Bitte versuche es später erneut.",
        )


def _create_token(user: User) -> str:
    payload = {"sub": str(user.id), "exp": int(time.time()) + _TOKEN_LIFETIME_SECONDS}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    token = auth_header[len("Bearer ") :].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Ungültiges Token") from None
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Ungültiges Token") from None
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Ungültiges Token")
    return user


@router.post("/register", response_model=Token)
def register(payload: Register, request: Request, db: Session = Depends(get_db)) -> Token:
    _enforce_rate_limit(request)
    email = payload.email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Bitte gib eine gültige E-Mail-Adresse ein")
    if db.query(User).filter(User.email == email).first() is not None:
        raise HTTPException(status_code=409, detail="Diese E-Mail-Adresse ist bereits registriert")
    user = User(email=email, password_hash=pwd_context.hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(access_token=_create_token(user), token_type="bearer")


@router.post("/login", response_model=Token)
def login(payload: Login, request: Request, db: Session = Depends(get_db)) -> Token:
    _enforce_rate_limit(request)
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-Mail oder Passwort ist falsch")
    return Token(access_token=_create_token(user), token_type="bearer")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=user.id, email=user.email)
