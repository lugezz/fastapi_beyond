from uuid import UUID

from pydantic import EmailStr, TypeAdapter
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.models.base import Base, TimestampMixin, uuid_pk_column


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = uuid_pk_column()
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    @validates("email")
    def validate_email(self, _: str, value: str) -> str:
        return TypeAdapter(EmailStr).validate_python(value)
