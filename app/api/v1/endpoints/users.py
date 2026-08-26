from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.users import (
    UserCreate,
    UserDetail,
    UserListItem,
    UserUpdate,
    UserVerifyPassword,
)
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
service = UserService()


@router.get("", response_model=Page[UserListItem], summary="List users")
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
) -> Page[UserListItem]:
    return await service.list_users(db, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserDetail, summary="Get user")
async def get_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetail:
    return await service.get_user(user_id, db)


@router.get("/by-email", response_model=UserDetail, summary="Get user by email")
async def get_user_by_email(
    email: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetail:
    return await service.get_user_by_email(email, db)


@router.post("/signup", response_model=UserDetail, status_code=status.HTTP_201_CREATED, summary="Sign up user")
async def signup_user(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetail:
    return await service.signup_user(data, db)


@router.patch("/{user_id}", response_model=UserDetail, summary="Update user")
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDetail:
    return await service.update_user(user_id, data, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    await service.delete_user(user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/verify-password", response_model=bool, summary="Verify user password")
async def verify_user_password(
    data: UserVerifyPassword,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    return await service.verify_user_password(data.email, data.password, db)
