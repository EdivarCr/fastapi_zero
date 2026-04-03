from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.core.database import get_section
from fastapi_zero.core.security import get_current_user
from fastapi_zero.exeptions import TodoNotFoundError, TodoNotInTrashError
from fastapi_zero.model.models import User as UserModel
from fastapi_zero.repository import TodoRepository
from fastapi_zero.schemas.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastapi_zero.services import TodoService

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_section)]
Current_user = Annotated[UserModel, Depends(get_current_user)]
Todo_filter = Annotated[FilterTodo, Query()]


def get_todo_service(session: Session) -> TodoService:
    return TodoService(TodoRepository(session))


TodoSvc = Annotated[TodoService, Depends(get_todo_service)]


@router.post('/', response_model=TodoPublic)
async def create_to_do(todo: TodoSchema, service: TodoSvc, user: Current_user):
    return await service.create(todo, user)


@router.get('/', response_model=TodoList)
async def list_to_dos(todo_query: Todo_filter, service: TodoSvc, user: Current_user):
    todos = await service.list(user.id, todo_query)
    return {'todos': list(todos)}


@router.get('/todo_trash', response_model=TodoList)
async def list_to_do_trash(
    todo_query: Todo_filter, service: TodoSvc, user: Current_user
):
    todos = await service.list_trash(user.id, todo_query)
    return {'todos': list(todos)}


@router.delete('/{id}/trash', response_model=Message)
async def delete_soft_to_do(id: int, service: TodoSvc, user: Current_user):
    try:
        await service.soft_delete(id, user.id)
        return {'message': 'Task moved to trash'}
    except TodoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))


@router.delete('/{id}/permanent', response_model=Message)
async def delete_to_dos(id: int, service: TodoSvc, user: Current_user):
    try:
        await service.permanent_delete(id, user.id)
        return {'message': 'Task has been deleted'}
    except TodoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))


@router.patch('/{id}', response_model=TodoPublic)
async def patch_to_do(
    id: int, service: TodoSvc, user: Current_user, todo_update: TodoUpdate
):
    try:
        return await service.update(id, user.id, todo_update)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))


@router.patch('/{id}/restore', response_model=TodoPublic)
async def restore_todo(id: int, service: TodoSvc, user: Current_user):
    try:
        return await service.restore(id, user.id)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except TodoNotInTrashError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
