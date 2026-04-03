from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.model.models import User


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.session.scalar(select(User).where(User.email == email))
