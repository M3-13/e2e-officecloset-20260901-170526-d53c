"""File storage helpers for uploaded clothing-item images.

Files are stored under ``<UPLOAD_DIR>/<user_id>/`` so that ``delete_user_files``
can remove a user's files without touching anyone else's. ``save_upload`` keeps
the documented ``(bytes, filename)`` signature; callers that know the owner may
pass ``user_id`` to place the file in that user's directory.
"""

import os
import shutil
import uuid

from .config import settings


def save_upload(content: bytes, filename: str, *, user_id: int | None = None) -> str:
    upload_dir = settings.upload_dir
    if user_id is not None:
        upload_dir = os.path.join(upload_dir, str(user_id))
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(filename)[1] or ""
    stored_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(upload_dir, stored_name)
    with open(path, "wb") as fh:
        fh.write(content)
    return path


def delete_file(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def delete_user_files(user_id: int) -> None:
    user_dir = os.path.join(settings.upload_dir, str(user_id))
    shutil.rmtree(user_dir, ignore_errors=True)
