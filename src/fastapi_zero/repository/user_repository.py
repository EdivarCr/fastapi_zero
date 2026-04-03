from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.model.models import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @property
    def model(self) -> type[User]:
        return User

    async def get_by_username(self, username: str) -> User | None:
        return await self.session.scalar(select(User).where(User.username == username))

    async def get_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))

    async def exists_by_username_or_email(
        self, username: str, email: str
    ) -> User | None:
        return await self.session.scalar(
            select(User).where((User.username == username) | (User.email == email))
        )
