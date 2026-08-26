from math import ceil
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.auth import generate_password_hash, verify_password
from app.models.users import User
from app.schemas.common import Page
from app.schemas.users import UserCreate, UserDetail, UserListItem, UserUpdate


class UserService:
    async def _get_user(self, user_id: str, db: AsyncSession) -> User:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def _ensure_unique_email(self, db: AsyncSession, email: str, exclude_user_id: str | None = None) -> None:
        query = select(User).filter(User.email == email)
        if exclude_user_id is not None:
            query = query.filter(User.id != exclude_user_id)
        result = await db.execute(query)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists")

    async def _commit_or_conflict(self, db: AsyncSession, detail: str) -> None:
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc

    def _to_detail(self, user: User) -> UserDetail:
        return UserDetail(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def list_users(self, db: AsyncSession, page: int = 1, page_size: int = 50) -> Page[UserListItem]:
        total = await db.scalar(select(func.count()).select_from(User))
        users = (
            await db.scalars(
                select(User)
                .order_by(User.email.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()
        items = [self._to_detail(user) for user in users]
        total_pages = ceil(total / page_size) if total else 0
        start = (page - 1) * page_size
        page_items = items[start:start + page_size]

        return Page[UserListItem](
            items=page_items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1 and total > 0,
        )

    async def get_user(self, user_id: str, db: AsyncSession) -> UserDetail:
        return self._to_detail(await self._get_user(user_id, db))

    async def _hash_password(self, password: str) -> str:
        # Implement your password hashing logic here
        # For example, using bcrypt:
        return generate_password_hash(password)

    async def signup_user(self, data: UserCreate, db: AsyncSession) -> UserDetail:
        await self._ensure_unique_email(db, str(data.email))
        password_hash = await self._hash_password(data.password)  # Assuming you have a method to hash passwords

        user = User(
            id=uuid4(),
            username=data.username,
            email=str(data.email),
            first_name=data.first_name,
            last_name=data.last_name,
            is_verified=data.is_verified,
            password_hash=password_hash,
        )
        db.add(user)
        await self._commit_or_conflict(db, detail="User data conflicts with an existing record")
        await db.refresh(user)
        return self._to_detail(user)

    async def _get_user_by_email(self, email: str, db: AsyncSession) -> User:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_user_by_email(self, email: str, db: AsyncSession) -> UserDetail:
        user = await self._get_user_by_email(email, db)
        return self._to_detail(user)

    async def update_user(self, user_id: str, data: UserUpdate, db: AsyncSession) -> UserDetail:
        user = await self._get_user(user_id, db)
        updates = data.model_dump(exclude_unset=True)

        email = updates.get("email")
        if email is not None:
            await self._ensure_unique_email(db, str(email), exclude_user_id=user_id)

        for field, value in updates.items():
            if field == "password":
                hashed_password = await self._hash_password(value)
                setattr(user, "password_hash", hashed_password)
            else:
                setattr(user, field, value)

        await self._commit_or_conflict(db, detail="User data conflicts with an existing record")
        await db.refresh(user)
        return self._to_detail(user)

    async def delete_user(self, user_id: str, db: AsyncSession) -> None:
        user = await self._get_user(user_id, db)
        await db.delete(user)
        await self._commit_or_conflict(db, detail="Cannot delete user due to related records")

    async def verify_user_password(self, email: str, password: str, db: AsyncSession) -> bool:
        user = await self._get_user_by_email(email, db)
        return verify_password(password, user.password_hash)
