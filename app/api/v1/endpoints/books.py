from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.books import BookItem, BookCreate, BookUpdate
from app.services.books import BookService

router = APIRouter(prefix="/books", tags=["books"])
service = BookService()


@router.get("", response_model=Page[BookItem])
async def get_books(
    db: Annotated[Session, Depends(get_db)],
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    return service.list_documents(db=db, search=search, page=page, page_size=page_size)


@router.get("/{book_id}", response_model=BookItem)
async def get_book(book_id: str, db: Annotated[Session, Depends(get_db)]):
    return service.get_book(book_id=book_id, db=db)


@router.post("", response_model=BookItem, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_create: BookCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return await service.create_book(book_create=book_create, db=db)


@router.patch("/{book_id}", response_model=BookItem)
async def update_book(
    book_id: str,
    book_update: BookUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    return await service.update_book(book_id=book_id, book_update=book_update, db=db)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    service.delete_book(book_id=book_id, db=db)
    return None
