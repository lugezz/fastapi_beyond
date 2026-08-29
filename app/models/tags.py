from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk_column


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"

    id: Mapped[UUID] = uuid_pk_column()
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    books = relationship("Book", secondary="book_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"


class BookTag(Base):
    __tablename__ = "book_tags"

    book_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("books.id"),
        primary_key=True,
        nullable=False,
    )
    tag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tags.id"),
        primary_key=True,
        nullable=False,
    )
