"""Add password reset token version

Revision ID: 20260908_100000
Revises: 2d8e5a91c3f4
Create Date: 2026-09-08 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260908_100000"
down_revision: str | Sequence[str] | None = "2d8e5a91c3f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_reset_version",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "password_reset_version")
