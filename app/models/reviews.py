from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk_column


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"

    id: Mapped[UUID] = uuid_pk_column()
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    book_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("books.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, content={self.rating}, rating={self.description})>"
