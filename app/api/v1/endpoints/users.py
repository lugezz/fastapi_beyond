from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import RoleChecker, get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.common import Page
from app.schemas.users import (
    UserCreate,
    UserDetail,
    UserListItem,
    UserMeResponse,
    UserUpdate,
)
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
service = UserService()
admin_required = RoleChecker(allowed_roles=["admin"])
admin_or_leader_required = RoleChecker(allowed_roles=["admin", "leader"])
user_required = RoleChecker(allowed_roles=["user", "leader", "admin"])


@router.get("/me", response_model=UserMeResponse, summary="Get current authenticated user")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[None, Depends(user_required)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserMeResponse:
    return await service.get_me(current_user, db)


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
    _: Annotated[None, Depends(admin_or_leader_required)],
) -> UserDetail:
    try:
        return await service.update_user(user_id, data, db)

    except StatementError as e:
        print(f"Database statement error: {e}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role.",
        )

    except ValueError as e:
        print(f"Error updating user: {e}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        print(f"Unexpected error updating user: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    await service.delete_user(user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
