import logging
from math import ceil
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.books import Book
from app.schemas.books import BookCreate, BookItem, BookUpdate
from app.schemas.common import Page

logger = logging.getLogger(__name__)


class BookService:
    async def list_books(
        self,
        db: AsyncSession,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Page[BookItem]:
        filters = []

        if search:
            filters.append(Book.title.ilike(f"%{search.strip()}%"))

        total = await db.scalar(select(func.count()).select_from(Book).where(*filters))
        books = (
            await db.scalars(
                select(Book)
                .where(*filters)
                .order_by(Book.published_date.desc(), Book.title.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()
        items = [self._to_item(book) for book in books]

        total_pages = ceil(total / page_size) if total else 0

        return Page[BookItem](
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1 and total > 0,
        )

    async def get_book(self, book_id: UUID, db: AsyncSession) -> BookItem:
        book = await self._get_book(book_id, db)
        return self._to_item(book)

    async def create_book(
        self,
        book_create: BookCreate,
        db: AsyncSession,
    ) -> BookItem:

        book = Book(
            id=uuid4(),
            title=book_create.title,
            author=book_create.author,
            publisher=book_create.publisher,
            published_date=book_create.published_date,
            page_count=book_create.page_count,
            language=book_create.language,
        )
        db.add(book)
        await db.commit()
        await db.refresh(book)

        return self._to_item(book)

    async def update_book(
        self,
        book_id: UUID,
        book_update: BookUpdate,
        db: AsyncSession,
    ) -> BookItem:
        book = await self._get_book(book_id, db)

        for field, value in book_update.model_dump(exclude_unset=True).items():
            setattr(book, field, value)

        await db.commit()
        await db.refresh(book)

        return self._to_item(book)

    async def delete_book(self, book_id: UUID, db: AsyncSession) -> None:
        book = await self._get_book(book_id, db)
        await db.delete(book)
        await db.commit()

    async def _get_book(self, book_id: UUID, db: AsyncSession) -> Book:
        book = await db.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
        return book

    @staticmethod
    def _to_item(book: Book) -> BookItem:
        return BookItem(
            id=book.id,
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            published_date=book.published_date,
            page_count=book.page_count,
            language=book.language,
        )
