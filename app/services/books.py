from math import ceil
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BookNotFoundError, BookPermissionError
from app.models.books import Book
from app.models.users import User, UserRole
from app.schemas.books import (
    BookCreate,
    BookDetail,
    BookItem,
    BookUpdate,
)
from app.schemas.common import Page
from app.schemas.reviews import ReviewItem


class BookService:
    async def list_books(
        self,
        db: AsyncSession,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
        user_id: UUID | None = None,
    ) -> Page[BookItem]:
        filters = []

        if user_id is not None:
            filters.append(Book.user_id == user_id)

        if search:
            filters.append(
                Book.title.ilike(f"%{search.strip()}%")
            )

        total = await db.scalar(
            select(func.count())
            .select_from(Book)
            .where(*filters)
        )

        books = (
            await db.scalars(
                select(Book)
                .where(*filters)
                .order_by(
                    Book.published_date.desc(),
                    Book.title.asc(),
                )
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
            has_prev=page > 1,
        )

    async def get_book_reviews(
        self,
        book_id: UUID,
        db: AsyncSession,
    ) -> list[ReviewItem]:
        from app.services.reviews import ReviewService

        review_service = ReviewService()

        result = await review_service.list_reviews(
            db=db,
            book_id=book_id,
        )

        return result.items

    async def get_book(
        self,
        book_id: UUID,
        db: AsyncSession,
    ) -> BookDetail:
        book = await self._get_book(book_id, db)

        return BookDetail(
            **self._to_item(book).model_dump(),
            created_at=book.created_at,
            updated_at=book.updated_at,
            reviews=await self.get_book_reviews(
                book_id=book_id,
                db=db,
            ),
        )

    async def create_book(
        self,
        data: BookCreate,
        db: AsyncSession,
        current_user: User,
    ) -> BookItem:
        book = Book(
            id=uuid4(),
            title=data.title,
            author=data.author,
            publisher=data.publisher,
            published_date=data.published_date,
            page_count=data.page_count,
            language=data.language,
            user_id=current_user.id,
        )

        db.add(book)

        await db.commit()
        await db.refresh(book)

        return self._to_item(book)

    async def update_book(
        self,
        book_id: UUID,
        data: BookUpdate,
        db: AsyncSession,
        current_user: User,
    ) -> BookItem:
        book = await self._get_book(book_id, db)

        self._ensure_can_manage_book(book, current_user)

        updates = data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(book, field, value)

        await db.commit()
        await db.refresh(book)

        return self._to_item(book)

    async def delete_book(
        self,
        book_id: UUID,
        db: AsyncSession,
        current_user: User,
    ) -> None:
        book = await self._get_book(book_id, db)

        self._ensure_can_manage_book(book, current_user)

        await db.delete(book)
        await db.commit()

    async def _get_book(
        self,
        book_id: UUID,
        db: AsyncSession,
    ) -> Book:
        book = await db.get(Book, book_id)

        if book is None:
            raise BookNotFoundError(book_id)

        return book

    @staticmethod
    def _ensure_can_manage_book(
        book: Book,
        current_user: User,
    ) -> None:
        if (
            book.user_id != current_user.id
            and current_user.role != UserRole.ADMIN
        ):
            raise BookPermissionError()

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
            user_id=book.user_id,
        )
