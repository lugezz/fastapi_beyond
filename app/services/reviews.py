import logging
from math import ceil
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.books import Book
from app.models.reviews import Review
from app.models.users import User
from app.schemas.common import Page
from app.schemas.reviews import ReviewCreate, ReviewItem, ReviewUpdate


logger = logging.getLogger(__name__)


class ReviewService:
    @staticmethod
    def _to_item(review: Review) -> ReviewItem:
        return ReviewItem(
            id=review.id,
            book_id=review.book_id,
            user_id=review.user_id,
            rating=review.rating,
            description=review.description,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    async def list_reviews(
        self,
        db: AsyncSession,
        book_id: UUID | None = None,
        user_id: UUID | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[ReviewItem]:
        """ List reviews with optional filtering by book_id and user_id, and pagination. """
        filters = []
        if book_id:
            filters.append(Review.book_id == book_id)
        if user_id:
            filters.append(Review.user_id == user_id)

        total = await db.scalar(select(func.count()).select_from(Review).where(*filters))
        reviews = (
            await db.scalars(
                select(Review)
                .where(*filters)
                .order_by(Review.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()

        items = [self._to_item(review) for review in reviews]
        total_pages = ceil(total / page_size) if total else 0

        return Page[ReviewItem](
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1 and total > 0,
        )

    async def get_review(self, review_id: UUID, db: AsyncSession) -> ReviewItem:
        """ Get a single review by its ID. """
        review = await db.get(Review, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with id {review_id} not found.",
            )
        return self._to_item(review)

    async def create_review(self, review_create: ReviewCreate, db: AsyncSession, user_id: UUID) -> ReviewItem:
        """ Create a new review. """
        book = await db.get(Book, review_create.book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {review_create.book_id} not found.",
            )
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )

        new_review = Review(
            id=uuid4(),
            book_id=review_create.book_id,
            user_id=user_id,
            rating=review_create.rating,
            description=review_create.description,
        )
        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)
        return self._to_item(new_review)

    async def update_review(self, review_id: UUID, review_update: ReviewUpdate, db: AsyncSession, user_id: UUID) -> ReviewItem:
        """ Update an existing review. """
        review = await db.get(Review, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with id {review_id} not found.",
            )
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        if review.user_id != user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this review.",
            )

        if review_update.rating is not None:
            review.rating = review_update.rating
        if review_update.description is not None:
            review.description = review_update.description

        await db.commit()
        await db.refresh(review)
        return self._to_item(review)

    async def delete_review(self, review_id: UUID, db: AsyncSession, user_id: UUID) -> None:
        """ Delete a review. """
        review = await db.get(Review, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with id {review_id} not found.",
            )
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        if review.user_id != user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this review.",
            )

        await db.delete(review)
        await db.commit()
