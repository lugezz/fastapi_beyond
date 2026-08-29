from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import RoleChecker, get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.books import BookCreate, BookItem, BookUpdate
from app.schemas.common import Page
from app.services.books import BookService

router = APIRouter(
    prefix="/books",
    tags=["books"],
    dependencies=[Depends(get_current_user)],
)
service = BookService()


admin_required = RoleChecker(allowed_roles=["admin"])


@router.get("", response_model=Page[BookItem])
async def get_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
    user_id: UUID | None = None,
):
    return await service.list_books(
        db=db,
        search=search,
        page=page,
        page_size=page_size,
        user_id=user_id,
    )


@router.get("/{book_id}", response_model=BookItem)
async def get_book(book_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await service.get_book(book_id=book_id, db=db)


@router.post("", response_model=BookItem, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_create: BookCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(admin_required)]
):
    try:
        return await service.create_book(book_create=book_create, db=db, user_id=current_user.id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while creating the book.", "details": str(e)},
        )


@router.patch("/{book_id}", response_model=BookItem)
async def update_book(
    book_id: UUID,
    book_update: BookUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(admin_required)]
):
    return await service.update_book(book_id=book_id, book_update=book_update, db=db, user_id=current_user.id)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(admin_required)]
):
    try:
        await service.delete_book(book_id=book_id, db=db, user_id=current_user.id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while deleting the book.", "details": str(e)},
        )
    return None
