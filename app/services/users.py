from math import ceil
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.common import Page
from app.schemas.users import UserCreate, UserDetail, UserListItem, UserUpdate


class UserService:
    def _get_user(self, user_id: str, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def _ensure_unique_email(self, db: Session, email: str, exclude_user_id: str | None = None) -> None:
        query = db.query(User).filter(User.email == email)
        if exclude_user_id is not None:
            query = query.filter(User.id != exclude_user_id)
        if query.one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists")

    def _commit_or_conflict(self, db: Session, detail: str) -> None:
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc

    def _to_detail(self, user: User) -> UserDetail:
        return UserDetail(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_verified=user.is_verified,
        )

    def list_users(self, db: Session, page: int = 1, page_size: int = 50) -> Page[UserListItem]:
        query = db.query(User)
        users = query.all()
        users.sort(key=lambda user: user.email.lower())

        items = [
            UserListItem(
                user_id=str(user.id),
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_verified=user.is_verified,
            )
            for user in users
        ]

        total = len(items)
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

    def get_user(self, user_id: str, db: Session) -> UserDetail:
        return self._to_detail(self._get_user(user_id, db))

    def create_user(self, data: UserCreate, db: Session) -> UserDetail:
        self._ensure_unique_email(db, str(data.email))

        user = User(
            id=uuid4(),
            username=data.username,
            email=str(data.email),
            first_name=data.first_name,
            last_name=data.last_name,
            is_verified=data.is_verified,
        )
        db.add(user)
        self._commit_or_conflict(db, detail="User data conflicts with an existing record")
        db.refresh(user)
        return self._to_detail(user)

    def update_user(self, user_id: str, data: UserUpdate, db: Session) -> UserDetail:
        user = self._get_user(user_id, db)
        updates = data.model_dump(exclude_unset=True)

        email = updates.get("email")
        if email is not None:
            self._ensure_unique_email(db, str(email), exclude_user_id=user_id)

        for field, value in updates.items():
            setattr(user, field, value)

        self._commit_or_conflict(db, detail="User data conflicts with an existing record")
        db.refresh(user)
        return self._to_detail(user)

    def delete_user(self, user_id: str, db: Session) -> None:
        user = self._get_user(user_id, db)
        db.delete(user)
        self._commit_or_conflict(db, detail="Cannot delete user due to related records")
