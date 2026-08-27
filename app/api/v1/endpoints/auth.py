from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenPair,
    VerifyPassword,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/login", response_model=TokenPair, summary="Placeholder login")
async def login(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    return await service.login(payload, db)


@router.post("/refresh", response_model=TokenPair, summary="Exchange a refresh token for a new token pair")
async def refresh(
    payload: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPair:
    return await service.refresh(payload, db)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT, summary="Update current user password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    await service.change_password(current_user, payload, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/verify-password", response_model=bool, summary="Verify user password")
async def verify_user_password(
    data: VerifyPassword,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    return await service.verify_user_password(data.email, data.password, db)
