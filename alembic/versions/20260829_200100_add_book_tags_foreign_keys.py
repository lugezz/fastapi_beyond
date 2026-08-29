"""Add book tags foreign keys

Revision ID: 2d8e5a91c3f4
Revises: 64d5747e7dfd
Create Date: 2026-08-29 20:01:00.000000

"""
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2d8e5a91c3f4"
down_revision: str | Sequence[str] | None = "64d5747e7dfd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        "fk_book_tags_book_id_books",
        "book_tags",
        "books",
        ["book_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_book_tags_tag_id_tags",
        "book_tags",
        "tags",
        ["tag_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_book_tags_tag_id_tags", "book_tags", type_="foreignkey")
    op.drop_constraint("fk_book_tags_book_id_books", "book_tags", type_="foreignkey")
