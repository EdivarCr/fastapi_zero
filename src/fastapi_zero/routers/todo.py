from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_section
from fastapi_zero.models import Todo
from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastapi_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_section)]
Current_user = Annotated[UserModel, Depends(get_current_user)]
Todo_filter = Annotated[FilterTodo, Query()]


@router.post('/', response_model=TodoPublic)
async def create_to_do(todo: TodoSchema, session: Session, user: Current_user):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
async def list_to_dos(todo_query: Todo_filter, session: Session, user: Current_user):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_query.title:
        query = query.filter(Todo.title.contains(todo_query.title))

    if todo_query.description:
        query = query.filter(Todo.description.contains(todo_query.description))

    if todo_query.state:
        query = query.filter(Todo.state == todo_query.state)

    todos = await session.scalars(
        query.offset(todo_query.offset).limit(todo_query.limit)
    )

    return {'todos': todos.all()}


@router.delete('/{id}', response_model=Message)
async def delete_soft_to_do(id: int, session: Session, user: Current_user):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found')

    todo.state = 'trash'
    await session.commit()
    return {'message': 'Task moved to trash'}


@router.delete('/{id}/permanent', response_model=Message)
async def delete_to_dos(id: int, session: Session, user: Current_user):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found')
    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted'}


@router.patch('/{id}', response_model=TodoPublic)
async def patch_to_do(
    id: int, session: Session, user: Current_user, todo_update: TodoUpdate
):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found')

    for key, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return todo


@router.get('/todo_trash', response_model=TodoList)
async def list_to_do_trash(
    todo_query: Todo_filter,
    session: Session,
    user: Current_user,
):

    query = select(Todo).where(Todo.user_id == user.id).where(Todo.state == 'trash')

    if todo_query.title:
        query = query.filter(Todo.title.contains(todo_query.title))

    if todo_query.description:
        query = query.filter(Todo.description.contains(todo_query.description))

    todos = await session.scalars(
        query.offset(todo_query.offset).limit(todo_query.limit)
    )

    return {'todos': todos.all()}


@router.patch('/{id}/restore', response_model=TodoPublic)
async def restore_todo(id: int, session: Session, user: Current_user):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id))

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Todo not found')
    if todo.state != 'trash':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Todo is not in trash'
        )
    todo.state = 'todo'  # Restaura para todo
    await session.commit()
    await session.refresh(todo)
    return todo
