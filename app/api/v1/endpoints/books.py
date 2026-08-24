
from fastapi import APIRouter, HTTPException, status

from app.schemas.books import Book, BookCreate, BookUpdate


router = APIRouter(prefix="/books", tags=["books"])
books_db: dict[int, Book] = {}


def get_next_book_id() -> int:
    if books_db:
        return max(books_db.keys()) + 1
    return 1


@router.get("", response_model=list[Book])
async def get_books():
    return list(books_db.values())


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int):
    if book_id in books_db:
        return books_db[book_id]
    raise HTTPException(status_code=404, detail="Book not found")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    book_id = get_next_book_id()
    new_book = Book(id=book_id, **book.model_dump())
    books_db[book_id] = new_book
    return {
        "message": f"Book '{new_book.title}' created successfully!",
        "book_id": book_id,
    }


@router.patch("/{book_id}", response_model=Book)
async def update_book(book_id: int, book: BookUpdate):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")

    stored_book = books_db[book_id]

    update_data = book.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(stored_book, field, value)

    return stored_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")

    books_db.pop(book_id)
    return None
