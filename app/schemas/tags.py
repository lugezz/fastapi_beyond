from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagItem(TagCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime


class TagUpdate(BaseModel):
    name: str


class BookTagItem(BaseModel):
    book_id: UUID
    tag_id: UUID


class TagAddItems(BaseModel):
    tags: list[TagCreate]


class BookTagAddItems(TagAddItems):
    book_id: UUID
