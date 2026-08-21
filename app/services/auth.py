from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.utils.security import hash_password, verify_password


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return db.scalar(
        select(User).where(
            User.email == email.lower()
        )
    )


def register_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    existing_user = get_user_by_email(
        db,
        email,
    )

    if existing_user:
        raise ValueError(
            "Email is already registered"
        )

    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        role=UserRole.USER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(
        db,
        email,
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user