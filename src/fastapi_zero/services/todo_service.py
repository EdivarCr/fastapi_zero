from typing import Sequence

from fastapi_zero.exeptions import TodoNotFoundError, TodoNotInTrashError
from fastapi_zero.model.models import Todo, TodoState
from fastapi_zero.model.models import User as UserModel
from fastapi_zero.repository import TodoRepository
from fastapi_zero.schemas.schemas import FilterTodo, TodoSchema, TodoUpdate


class TodoService:
    def __init__(self, repo: TodoRepository):
        self.repo = repo

    async def create(self, todo_in: TodoSchema, user: UserModel) -> Todo:
        db_todo = Todo(
            title=todo_in.title,
            description=todo_in.description,
            state=todo_in.state,
            user_id=user.id,
        )
        return await self.repo.create(db_todo)

    async def list(self, user_id: int, filters: FilterTodo) -> Sequence[Todo]:
        return await self.repo.get_by_user(user_id, filters)

    async def list_trash(self, user_id: int, filters: FilterTodo) -> Sequence[Todo]:
        return await self.repo.get_trash_by_user(user_id, filters)

    async def soft_delete(self, id: int, user_id: int) -> None:
        todo = await self.repo.get_by_id_and_user(id, user_id)
        if not todo:
            raise TodoNotFoundError()

        todo.state = TodoState.trash
        await self.repo.update(todo)

    async def permanent_delete(self, id: int, user_id: int) -> None:
        todo = await self.repo.get_by_id_and_user(id, user_id)
        if not todo:
            raise TodoNotFoundError()

        await self.repo.delete(todo)

    async def update(self, id: int, user_id: int, todo_update: TodoUpdate) -> Todo:
        todo = await self.repo.get_by_id_and_user(id, user_id)
        if not todo:
            raise TodoNotFoundError()

        for key, value in todo_update.model_dump(exclude_unset=True).items():
            setattr(todo, key, value)

        return await self.repo.update(todo)

    async def restore(self, id: int, user_id: int) -> Todo:
        todo = await self.repo.get_by_id_and_user(id, user_id)
        if not todo:
            raise TodoNotFoundError()

        if todo.state != TodoState.trash:
            raise TodoNotInTrashError()

        todo.state = TodoState.todo
        return await self.repo.update(todo)
