from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import RoleChecker, get_current_user
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.tags import BookTagAddItems, TagCreate, TagItem, TagUpdate
from app.services.tags import TagService

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    dependencies=[Depends(get_current_user)],
)
service = TagService()


user_required = RoleChecker(allowed_roles=["user", "leader", "admin"])
admin_required = RoleChecker(allowed_roles=["admin"])


@router.get("", response_model=Page[TagItem])
async def get_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 50,
    book_id: UUID | None = None,
):
    return await service.list_tags(
        db=db,
        page=page,
        page_size=page_size,
        book_id=book_id,
    )


@router.get("/{tag_id}", response_model=TagItem)
async def get_tag(tag_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await service.get_tag(tag_id=tag_id, db=db)


@router.post("", response_model=TagItem, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_create: TagCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await service.create_tag(data=tag_create, db=db)


@router.post("/add-tags", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def add_tags(
    book_n_tags: BookTagAddItems,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await service.add_tags_to_book(book_id=book_n_tags.book_id, data=book_n_tags, db=db)


@router.patch("/{tag_id}", response_model=TagItem)
async def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await service.update_tag(tag_id=tag_id, data=tag_update, db=db)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await service.delete_tag(tag_id=tag_id, db=db)
