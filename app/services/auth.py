from fastapi import HTTPException, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    # generate_invitation_token,
    # hash_invitation_token,
    hash_password,
    verify_password,
)
from app.models.users import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenPair,
)


class AuthService:
    async def login(self, payload: LoginRequest, db: AsyncSession) -> TokenPair:
        user = await db.scalar(
            select(User).where(User.email == payload.email)
        )
        if user is None or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        subject = payload.email
        return TokenPair(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )

    async def refresh(self, payload: RefreshTokenRequest, db: AsyncSession) -> TokenPair:
        invalid_token = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            claims = decode_token(payload.refresh_token)
        except InvalidTokenError as exc:
            raise invalid_token from exc

        subject = claims.get("sub")
        if not subject or claims.get("type") != "refresh":
            raise invalid_token

        user = await db.scalar(
            select(User).where(User.email == subject)
        )
        if user is None:
            raise invalid_token

        return TokenPair(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )

    async def change_password(self, current_user: User, payload: ChangePasswordRequest, db: AsyncSession) -> None:
        if current_user.password_hash is None or not verify_password(payload.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is invalid",
            )

        current_user.password_hash = hash_password(payload.new_password)
        await db.commit()

    async def verify_user_password(self, email: str, password: str, db: AsyncSession) -> bool:
        user = await db.scalar(
            select(User).where(User.email == email)
        )
        if user is None or not user.password_hash:
            return False
        return verify_password(password, user.password_hash)
