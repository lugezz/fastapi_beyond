import logging
from math import ceil
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.books import Book
from app.schemas.books import BookCreate, BookUpdate, BookItem
from app.schemas.common import Page

logger = logging.getLogger(__name__)


class BookService:
    def list_documents(
        self,
        db: Session,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Page[BookItem]:
        query = db.query(Book)

        if search:
            query = query.filter(Book.title.ilike(f"%{search.strip()}%"))

        books = query.order_by(Book.published_date.desc(), Book.title.asc()).all()
        items = [self._to_item(book) for book in books]

        total = len(items)
        total_pages = ceil(total / page_size) if total else 0
        start = (page - 1) * page_size

        return Page[BookItem](
            items=items[start:start + page_size],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1 and total > 0,
        )

    def get_book(self, book_id: str, db: Session) -> BookItem:
        book = self._get_book(book_id, db)
        return self._to_item(book)

    async def create_book(
        self,
        book_create: BookCreate,
        db: Session,
    ) -> BookItem:

        book_id = str(uuid4())

        book = Book(
            id=book_id,
            title=book_create.title,
            author=book_create.author,
            publisher=book_create.publisher,
            published_date=book_create.published_date,
            page_count=book_create.page_count,
            language=book_create.language,
        )
        db.add(book)
        db.commit()
        db.refresh(book)

        return self._to_item(book)

    async def update_book(
        self,
        book_id: str,
        book_update: BookUpdate,
        db: Session,
    ) -> BookItem:
        book = self._get_book(book_id, db)

        title = book_update.title if book_update.title is not None else book.title
        author = book_update.author if book_update.author is not None else book.author
        publisher = book_update.publisher if book_update.publisher is not None else book.publisher
        published_date = book_update.published_date if book_update.published_date is not None else book.published_date
        page_count = book_update.page_count if book_update.page_count is not None else book.page_count
        language = book_update.language if book_update.language is not None else book.language

        book.title = title
        book.author = author
        book.publisher = publisher
        book.published_date = published_date
        book.page_count = page_count
        book.language = language

        db.add(book)
        db.commit()
        db.refresh(book)

        return self._to_item(book)

    def delete_book(self, book_id: str, db: Session) -> None:
        book = self._get_book(book_id, db)
        db.delete(book)
        db.commit()
