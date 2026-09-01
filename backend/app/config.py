"""Application configuration, read lazily from environment variables.

Every value has a runnable default so a freshly cloned repo starts without any
manual setup. ``SECRET_KEY`` is the one value with no real default: the skeleton
does not sign tokens yet, so an empty string is enough to boot and the auth
ticket validates it at startup.
"""

import os


class Settings:
    @property
    def database_url(self) -> str:
        return os.environ.get("DATABASE_URL", "sqlite:///./wardrobe.db")

    @property
    def secret_key(self) -> str:
        return os.environ.get("SECRET_KEY", "")

    @property
    def upload_dir(self) -> str:
        return os.environ.get("UPLOAD_DIR", "./uploads")

    @property
    def frontend_origin(self) -> str:
        return os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    @property
    def max_upload_mb(self) -> int:
        return int(os.environ.get("MAX_UPLOAD_MB", "5"))


settings = Settings()
