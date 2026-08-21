import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select

from app.config.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password, verify_password


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin@12345"


def seed_admin():
    db = SessionLocal()

    try:
        # Check whether admin already exists
        existing_admin = db.scalar(
            select(User).where(User.email == ADMIN_EMAIL)
        )

        if existing_admin:
            print(f"Admin already exists: {existing_admin.email}")
            print(f"Admin role: {existing_admin.role}")
            print(
                "Password verification:",
                verify_password(
                    ADMIN_PASSWORD,
                    existing_admin.password_hash,
                ),
            )
            return

        # Create admin user
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("Admin created successfully.")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"Role: {admin.role.value}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()

