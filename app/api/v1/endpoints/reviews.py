from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import RoleChecker, get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.common import Page
from app.schemas.reviews import ReviewCreate, ReviewItem, ReviewUpdate
from app.services.reviews import ReviewService

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Depends(get_current_user)],
)
service = ReviewService()


user_required = RoleChecker(allowed_roles=["user", "leader", "admin"])
admin_required = RoleChecker(allowed_roles=["admin"])


@router.get("", response_model=Page[ReviewItem])
async def get_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 50,
    book_id: UUID | None = None,
    user_id: UUID | None = None,
):
    try:
        return await service.list_reviews(
            db=db,
            book_id=book_id,
            user_id=user_id,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "An error occurred while fetching reviews.", "details": str(e)},
        )


@router.get("/{review_id}", response_model=ReviewItem)
async def get_review(review_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await service.get_review(review_id=review_id, db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "An error occurred while fetching the review.", "details": str(e)},
        )


@router.post("", response_model=ReviewItem, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_create: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(user_required)]
):
    try:
        return await service.create_review(review_create=review_create, db=db, user_id=current_user.id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while creating the review.", "details": str(e)},
        )


@router.patch("/{review_id}", response_model=ReviewItem)
async def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(user_required)]
):
    return await service.update_review(review_id=review_id, review_update=review_update, db=db, user_id=current_user.id)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(user_required)]
):
    try:
        await service.delete_review(review_id=review_id, db=db, user_id=current_user.id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Integrity error occurred while deleting the review.", "details": str(e)},
        )
    return None
