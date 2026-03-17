from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import User


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
    }
