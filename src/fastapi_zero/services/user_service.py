from typing import Sequence

from fastapi_zero.core.security import get_password_hash
from fastapi_zero.exeptions import (
    ForbiddenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from fastapi_zero.model.models import User as UserModel
from fastapi_zero.repository import UserRepository
from fastapi_zero.schemas.schemas import User


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create(self, user_in: User) -> UserModel:
        existing = await self.repo.exists_by_username_or_email(
            user_in.username, user_in.email
        )
        if existing:
            if existing.username == user_in.username:
                raise UserAlreadyExistsError('Username')
            raise UserAlreadyExistsError('Email')

        db_user = UserModel(
            username=user_in.username,
            email=user_in.email,
            password=get_password_hash(user_in.password),
        )
        return await self.repo.create(db_user)

    async def list(self, limit: int = 10, offset: int = 0) -> Sequence[UserModel]:
        return await self.repo.get_all(limit, offset)

    async def get(self, user_id: int) -> UserModel:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError('User not found by id')
        return user

    async def update(
        self, user_id: int, current_user: UserModel, user_in: User
    ) -> UserModel:
        if current_user.id != user_id:
            raise ForbiddenError()

        current_user.username = user_in.username
        current_user.email = user_in.email
        current_user.password = get_password_hash(user_in.password)
        return await self.repo.update(current_user)

    async def delete(self, user_id: int, current_user: UserModel) -> None:
        if current_user.id != user_id:
            raise ForbiddenError()
        await self.repo.delete(current_user)
