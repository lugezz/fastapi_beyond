from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    book_id: UUID
    rating: int = Field(ge=1, le=5)
    description: str | None = None


class ReviewItem(ReviewCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    description: str | None = None
