from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.model.models import Todo
from fastapi_zero.schemas.schemas import FilterTodo

from .base_repository import BaseRepository


class TodoRepository(BaseRepository[Todo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[Todo]:
        return Todo

    async def get_by_user(self, user_id: int, filters: FilterTodo) -> Sequence[Todo]:
        query = select(Todo).where(Todo.user_id == user_id)

        if filters.title:
            query = query.filter(Todo.title.contains(filters.title))

        if filters.description:
            query = query.filter(Todo.description.contains(filters.description))

        if filters.state:
            query = query.filter(Todo.state == filters.state)

        result = await self.session.scalars(
            query.offset(filters.offset).limit(filters.limit)
        )
        return result.all()

    async def get_by_id_and_user(self, id: int, user_id: int) -> Todo | None:
        return await self.session.scalar(
            select(Todo).where(Todo.user_id == user_id, Todo.id == id)
        )

    async def get_trash_by_user(
        self, user_id: int, filters: FilterTodo
    ) -> Sequence[Todo]:
        query = select(Todo).where(Todo.user_id == user_id).where(Todo.state == 'trash')

        if filters.title:
            query = query.filter(Todo.title.contains(filters.title))

        if filters.description:
            query = query.filter(Todo.description.contains(filters.description))

        result = await self.session.scalars(
            query.offset(filters.offset).limit(filters.limit)
        )
        return result.all()
