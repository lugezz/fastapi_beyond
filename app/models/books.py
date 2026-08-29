from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk_column


class Book(TimestampMixin, Base):
    __tablename__ = "books"

    id: Mapped[UUID] = uuid_pk_column()
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    author: Mapped[str | None] = mapped_column(String(160), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(160), nullable=True)
    published_date: Mapped[date] = mapped_column(Date, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(60), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    user = relationship("User", back_populates="books")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title={self.title}, author={self.author})>"
