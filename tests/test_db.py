from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(username='testuser', email='teste@teste.com', password='teste123')

        session.add(user)
        await session.commit()

        assert user.username == 'testuser'

    user_query = await session.scalar(select(User).where(User.username == 'testuser'))

    assert asdict(user_query) == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'teste123',
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session, user):
    todo = Todo(
        title='Test Todo', description='Desc Todo', state='draft', user_id=user.id
    )

    session.add(todo)
    await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'description': 'Desc Todo',
        'id': 1,
        'state': 'draft',
        'title': 'Test Todo',
        'user_id': 1,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user: User):
    todo = Todo(
        title='Titulo Teste',
        description='Desc Teste',
        state='doing',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
