from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.models.user import User


_DEFAULT_SECRETS = {
    "your-jwt-secret-key",
    "your-super-secret-key-change-this",
    "",
}


def verify_device_key_value(provided_key: Optional[str], expected_key: str) -> None:
    if not expected_key or provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device key",
        )


async def verify_device_key(x_device_key: Optional[str] = Header(default=None)) -> None:
    verify_device_key_value(x_device_key, settings.DEVICE_API_KEY)


def assert_safe_production_settings(active_settings=settings) -> None:
    if active_settings.APP_ENV != "production":
        return

    unsafe = []
    if active_settings.DEBUG:
        unsafe.append("DEBUG must be false")
    if active_settings.JWT_SECRET_KEY in _DEFAULT_SECRETS:
        unsafe.append("JWT_SECRET_KEY must be set")
    if active_settings.SECRET_KEY in _DEFAULT_SECRETS:
        unsafe.append("SECRET_KEY must be set")
    if not active_settings.DEVICE_API_KEY:
        unsafe.append("DEVICE_API_KEY must be set")

    if unsafe:
        raise RuntimeError("Unsafe production settings: " + "; ".join(unsafe))


def require_privileged_user(user: User) -> None:
    if getattr(user, "role", None) not in {"admin", "doctor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
