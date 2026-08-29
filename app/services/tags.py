from math import ceil
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    BookNotFoundError,
    TagAlreadyExistsError,
    TagNotFoundError,
)
from app.models.books import Book
from app.models.tags import Tag
from app.schemas.common import Page
from app.schemas.tags import (
    TagAddItems,
    TagCreate,
    TagItem,
    TagUpdate,
)


class TagService:
    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().lower()

    @staticmethod
    def _to_item(tag: Tag) -> TagItem:
        return TagItem(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
        )

    async def list_tags(
        self,
        db: AsyncSession,
        name: str | None = None,
        page: int = 1,
        page_size: int = 50,
        book_id: UUID | None = None,
    ) -> Page[TagItem]:
        filters = []

        if name:
            filters.append(
                Tag.name.ilike(f"%{name.strip()}%")
            )

        if book_id is not None:
            filters.append(
                Tag.books.any(id=book_id)
            )

        total = await db.scalar(
            select(func.count())
            .select_from(Tag)
            .where(*filters)
        )

        tags = (
            await db.scalars(
                select(Tag)
                .where(*filters)
                .order_by(Tag.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()

        items = [self._to_item(tag) for tag in tags]

        total_pages = ceil(total / page_size) if total else 0

        return Page[TagItem](
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    async def get_tag_by_name(
        self,
        name: str,
        db: AsyncSession,
    ) -> Tag | None:
        normalized_name = self._normalize_name(name)

        return await db.scalar(
            select(Tag).where(Tag.name == normalized_name)
        )

    async def get_tag(
        self,
        tag_id: UUID,
        db: AsyncSession,
    ) -> TagItem:
        tag = await db.get(Tag, tag_id)

        if tag is None:
            raise TagNotFoundError()

        return self._to_item(tag)

    async def create_tag(
        self,
        data: TagCreate,
        db: AsyncSession,
    ) -> TagItem:
        name = self._normalize_name(data.name)

        existing_tag = await self.get_tag_by_name(
            name=name,
            db=db,
        )

        if existing_tag is not None:
            raise TagAlreadyExistsError()

        tag = Tag(
            id=uuid4(),
            name=name,
        )

        db.add(tag)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise TagAlreadyExistsError() from exc

        await db.refresh(tag)

        return self._to_item(tag)

    async def update_tag(
        self,
        tag_id: UUID,
        data: TagUpdate,
        db: AsyncSession,
    ) -> TagItem:
        tag = await db.get(Tag, tag_id)

        if tag is None:
            raise TagNotFoundError()

        if data.name is not None:
            name = self._normalize_name(data.name)

            if name != tag.name:
                existing_tag = await self.get_tag_by_name(
                    name=name,
                    db=db,
                )

                if existing_tag is not None:
                    raise TagAlreadyExistsError()

                tag.name = name

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise TagAlreadyExistsError() from exc

        await db.refresh(tag)

        return self._to_item(tag)

    async def delete_tag(
        self,
        tag_id: UUID,
        db: AsyncSession,
    ) -> None:
        tag = await db.get(Tag, tag_id)

        if tag is None:
            raise TagNotFoundError()

        await db.delete(tag)
        await db.commit()

    async def add_tags_to_book(
        self,
        book_id: UUID,
        data: TagAddItems,
        db: AsyncSession,
    ) -> list[TagItem]:
        book = await db.scalar(
            select(Book)
            .where(Book.id == book_id)
            .options(selectinload(Book.tags))
        )

        if book is None:
            raise BookNotFoundError()

        tag_names = {
            self._normalize_name(tag.name)
            for tag in data.tags
        }

        if not tag_names:
            return []

        existing_tags = (
            await db.scalars(
                select(Tag).where(Tag.name.in_(tag_names))
            )
        ).all()

        tags_by_name = {
            tag.name: tag
            for tag in existing_tags
        }

        tags_to_add = []

        for name in tag_names:
            tag = tags_by_name.get(name)

            if tag is None:
                tag = Tag(
                    id=uuid4(),
                    name=name,
                )
                db.add(tag)

            if tag not in book.tags:
                book.tags.append(tag)

            tags_to_add.append(tag)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise TagAlreadyExistsError() from exc

        return [
            self._to_item(tag)
            for tag in tags_to_add
        ]
