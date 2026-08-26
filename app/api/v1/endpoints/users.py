from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.users import UserCreate, UserDetail, UserListItem, UserUpdate
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
service = UserService()


@router.get("", response_model=Page[UserListItem], summary="List users")
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
) -> Page[UserListItem]:
    return service.list_users(db, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserDetail, summary="Get user")
async def get_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetail:
    return service.get_user(user_id, db)


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED, summary="Create user")
async def create_user(
    data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetail:
    return service.create_user(data, db)


@router.patch("/{user_id}", response_model=UserDetail, summary="Update user")
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> UserDetail:
    return service.update_user(user_id, data, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service.delete_user(user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
