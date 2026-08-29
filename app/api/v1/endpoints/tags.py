from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import RoleChecker, get_current_user
from app.core.exceptions import (
    BookNotFoundError,
    TagNotFoundError,
    TagAlreadyExistsError,
)
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.tags import TagAddItems, TagCreate, TagItem, TagUpdate
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
    try:
        return await service.list_tags(
            db=db,
            page=page,
            page_size=page_size,
            book_id=book_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "An error occurred while fetching tags.", "details": str(e)},
        )


@router.get("/{tag_id}", response_model=TagItem)
async def get_tag(tag_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await service.get_tag(tag_id=tag_id, db=db)
    except TagNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "An error occurred while fetching the tag.", "details": str(e)},
        )


@router.post("", response_model=TagItem, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_create: TagCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return await service.create_tag(tag_create=tag_create, db=db)
    except TagAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_create.name}' already exists.",
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while creating the tag.", "details": str(e)},
        )


@router.post("/add-tags", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def add_tags(
    book_id: UUID,
    tag_items: TagAddItems,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        await service.add_tags_to_book(book_id=book_id, data=tag_items, db=db)
    except BookNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    except TagNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while adding tags to the book.", "details": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "An error occurred while adding tags to the book.", "details": str(e)},
        )
    return None


@router.patch("/{tag_id}", response_model=TagItem)
async def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return await service.update_tag(tag_id=tag_id, tag_update=tag_update, db=db)
    except TagNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found",
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while updating the tag.", "details": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "An error occurred while updating the tag.", "details": str(e)},
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        await service.delete_tag(tag_id=tag_id, db=db)
    except TagNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found",
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while deleting the tag.", "details": str(e)},
        )
    return None
