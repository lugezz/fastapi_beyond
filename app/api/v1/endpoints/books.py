from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.books import BookCreate, BookItem, BookUpdate
from app.schemas.common import Page
from app.services.books import BookService

router = APIRouter(prefix="/books", tags=["books"])
service = BookService()


@router.get("", response_model=Page[BookItem])
async def get_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    return await service.list_documents(db=db, search=search, page=page, page_size=page_size)


@router.get("/{book_id}", response_model=BookItem)
async def get_book(book_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await service.get_book(book_id=book_id, db=db)


@router.post("", response_model=BookItem, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_create: BookCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await service.create_book(book_create=book_create, db=db)


@router.patch("/{book_id}", response_model=BookItem)
async def update_book(
    book_id: UUID,
    book_update: BookUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await service.update_book(book_id=book_id, book_update=book_update, db=db)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await service.delete_book(book_id=book_id, db=db)
    return None
