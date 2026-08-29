from math import ceil
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserEmailAlreadyExistsError, UserNotFoundError
from app.core.security import hash_password
from app.models.books import Book
from app.models.users import User, UserRole
from app.schemas.books import BookItem
from app.schemas.common import Page
from app.schemas.reviews import ReviewItem
from app.schemas.users import (
    UserCapabilities,
    UserCreate,
    UserDetail,
    UserListItem,
    UserMeResponse,
    UserUpdate,
)


class UserService:
    async def get_user_books(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[Book]:
        result = await db.scalars(
            select(Book).where(Book.user_id == user_id)
        )
        return result.all()

    def _book_details(self, book: Book) -> BookItem:
        return BookItem(
            id=book.id,
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            published_date=book.published_date,
            page_count=book.page_count,
            language=book.language,
            user_id=book.user_id,
        )

    async def get_me(
        self,
        current_user: User,
        db: AsyncSession,
    ) -> UserMeResponse:
        books = await self.get_user_books(current_user.id, db)
        reviews = await self.get_user_reviews(current_user.id, db)

        return UserMeResponse(
            user_id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            is_verified=current_user.is_verified,
            role=current_user.role,
            capabilities=self._build_capabilities(current_user),
            books=[self._book_details(book) for book in books],
            reviews=reviews,
        )

    def _build_capabilities(self, user: User) -> UserCapabilities:
        return UserCapabilities(
            can_manage_users=user.role == UserRole.ADMIN,
            can_manage_books=user.role in {
                UserRole.ADMIN,
                UserRole.LEADER,
            },
        )

    async def _get_user(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> User:
        user = await db.scalar(
            select(User).where(User.id == user_id)
        )

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    async def _ensure_unique_email(
        self,
        db: AsyncSession,
        email: str,
        exclude_user_id: UUID | None = None,
    ) -> None:
        query = select(User).where(User.email == email)

        if exclude_user_id is not None:
            query = query.where(User.id != exclude_user_id)

        user = await db.scalar(query)

        if user is not None:
            raise UserEmailAlreadyExistsError(email)

    async def _commit_or_conflict(
        self,
        db: AsyncSession,
    ) -> None:
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise UserEmailAlreadyExistsError() from exc

    def _to_detail(self, user: User) -> UserDetail:
        return UserDetail(
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _to_list_item(self, user: User) -> UserListItem:
        return UserListItem(
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_verified=user.is_verified,
        )

    async def list_users(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
    ) -> Page[UserListItem]:
        total = await db.scalar(
            select(func.count()).select_from(User)
        )

        users = (
            await db.scalars(
                select(User)
                .order_by(User.email.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()

        items = [self._to_list_item(user) for user in users]

        total_pages = ceil(total / page_size) if total else 0

        return Page[UserListItem](
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    async def get_user_reviews(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[ReviewItem]:
        from app.services.reviews import ReviewService

        review_service = ReviewService()
        result = await review_service.list_reviews(
            db=db,
            user_id=user_id,
        )

        return result.items

    async def get_user(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> UserDetail:
        user = await self._get_user(user_id, db)
        return self._to_detail(user)

    async def signup_user(
        self,
        data: UserCreate,
        db: AsyncSession,
    ) -> UserDetail:
        email = str(data.email)

        await self._ensure_unique_email(
            db=db,
            email=email,
        )

        user = User(
            id=uuid4(),
            username=data.username,
            email=email,
            first_name=data.first_name,
            last_name=data.last_name,
            is_verified=False,
            password_hash=hash_password(data.password),
        )

        db.add(user)

        await self._commit_or_conflict(db)
        await db.refresh(user)

        return self._to_detail(user)

    async def _get_user_by_email(
        self,
        email: str,
        db: AsyncSession,
    ) -> User:
        user = await db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_user_by_email(
        self,
        email: str,
        db: AsyncSession,
    ) -> UserDetail:
        user = await self._get_user_by_email(email, db)
        return self._to_detail(user)

    async def update_user(
        self,
        user_id: UUID,
        data: UserUpdate,
        db: AsyncSession,
    ) -> UserDetail:
        user = await self._get_user(user_id, db)
        updates = data.model_dump(exclude_unset=True)

        email = updates.get("email")

        if email is not None:
            await self._ensure_unique_email(
                db=db,
                email=str(email),
                exclude_user_id=user_id,
            )
            updates["email"] = str(email)

        password = updates.pop("password", None)

        if password is not None:
            user.password_hash = hash_password(password)

        for field, value in updates.items():
            setattr(user, field, value)

        await self._commit_or_conflict(db)
        await db.refresh(user)

        return self._to_detail(user)

    async def delete_user(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> None:
        user = await self._get_user(user_id, db)

        await db.delete(user)

        await self._commit_or_conflict(db)
