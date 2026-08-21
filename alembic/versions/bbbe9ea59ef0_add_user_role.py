"""add user role

Revision ID: bbbe9ea59ef0
Revises: 2df59e57f0ba
Create Date: 2026-08-10 19:18:25.423842

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "bbbe9ea59ef0"
down_revision: Union[str, Sequence[str], None] = "2df59e57f0ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    user_role_enum = sa.Enum(
        "user",
        "admin",
        name="user_role",
    )

    user_role_enum.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE users SET role = 'user' WHERE role IS NULL"
    )

    op.alter_column(
        "users",
        "role",
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "role",
    )

    sa.Enum(
        "user",
        "admin",
        name="user_role",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )