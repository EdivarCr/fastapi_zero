from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_section
from fastapi_zero.models import Todo
from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import FilterTodo, TodoList, TodoPublic, TodoSchema
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
        query = query.filter(Todo.title.contains.todo_query.title)

    if todo_query.description:
        query = query.filter(Todo.description.contains.todo_query.description)

    if todo_query.state:
        query = query.filter(Todo.state.contains.todo_query.state)

    todos = await session.scalars(
        query.offset(todo_query.offset).limit(todo_query.limit)
    )

    return {'todos': todos.all()}
