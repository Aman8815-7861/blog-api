import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config.settings import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    password_hash_value: str,
) -> bool:
    return password_hash.verify(
        password,
        password_hash_value,
    )


def create_access_token(
    user_id: uuid.UUID,
    role: str,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    user_id = payload.get("sub")
    role = payload.get("role")

    if user_id is None:
        raise ValueError("Invalid token")

    if role is None:
        raise ValueError("Invalid token")

    try:
        uuid.UUID(user_id)
    except ValueError as exc:
        raise ValueError("Invalid user ID") from exc

    return payload