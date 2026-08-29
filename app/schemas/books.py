from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.reviews import ReviewItem


class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookItem(BookCreate):
    id: UUID
    user_id: UUID


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = None
    language: str | None = None


class BookDetail(BookItem):
    created_at: datetime
    updated_at: datetime
    reviews: list[ReviewItem] = []
