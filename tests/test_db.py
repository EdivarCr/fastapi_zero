from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(username='testuser', email='teste@teste.com', password='teste123')

        session.add(user)
        session.commit()

        assert user.username == 'testuser'

        user_query = session.scalar(select(User).where(User.username == 'testuser'))

    assert asdict(user_query) == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'teste123',
        'created_at': time,
        'updated_at': time,
    }
