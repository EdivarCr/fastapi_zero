from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from fastapi_zero.models import Todo, TodoState


def test_create_to_do(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_lits_to_dos(session, token, client, user):
    expected_to_dos = 5
    session.add_all(todo_factory.create_batch(5, user_id=user.id))

    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_to_dos


class todo_factory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_list_to_dos_filter_title(session, token, client, user):
    expected_to_dos = 2
    session.add_all([
        todo_factory(title='Comprar leite', user_id=user.id),
        todo_factory(title='Comprar pão', user_id=user.id),
        todo_factory(title='Estudar Python', user_id=user.id),
    ])
    await session.commit()

    response = client.get(
        '/todos/?title=Comprar',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_list_to_dos_filter_description(session, token, client, user):
    expected_to_dos = 2
    session.add_all([
        todo_factory(title='Todo 1', description='urgente fazer hoje', user_id=user.id),
        todo_factory(
            title='Todo 2', description='urgente para amanhã', user_id=user.id
        ),
        todo_factory(title='Todo 3', description='pode esperar', user_id=user.id),
    ])
    await session.commit()

    response = client.get(
        '/todos/?description=urgente',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_list_to_dos_filter_state(session, token, client, user):
    expected_to_dos = 2
    session.add_all([
        todo_factory(title='Todo 1', state=TodoState.done, user_id=user.id),
        todo_factory(title='Todo 2', state=TodoState.done, user_id=user.id),
        todo_factory(title='Todo 3', state=TodoState.draft, user_id=user.id),
        todo_factory(title='Todo 4', state=TodoState.doing, user_id=user.id),
    ])
    await session.commit()

    response = client.get(
        '/todos/?state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_list_to_dos_filter_combined(session, token, client, user):
    expected_to_dos = 1
    session.add_all([
        todo_factory(
            title='Tarefa casa',
            description='limpar',
            state=TodoState.todo,
            user_id=user.id,
        ),
        todo_factory(
            title='Tarefa trabalho',
            description='relatório',
            state=TodoState.todo,
            user_id=user.id,
        ),
        todo_factory(
            title='Tarefa casa',
            description='organizar',
            state=TodoState.done,
            user_id=user.id,
        ),
    ])
    await session.commit()

    response = client.get(
        '/todos/?title=Tarefa casa&state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_list_to_dos_pagination_offset(session, token, client, user):
    expected_to_dos = 5
    session.add_all([
        todo_factory(title=f'Todo {i}', user_id=user.id) for i in range(10)
    ])
    await session.commit()

    response = client.get(
        '/todos/?offset=5',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_list_to_dos_pagination_limit(session, token, client, user):
    expected_to_dos = 3
    session.add_all([
        todo_factory(title=f'Todo {i}', user_id=user.id) for i in range(10)
    ])
    await session.commit()

    response = client.get(
        '/todos/?limit=3',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_list_to_dos_pagination_offset_and_limit(session, token, client, user):
    expected_to_dos = 3
    session.add_all([
        todo_factory(title=f'Todo {i}', user_id=user.id) for i in range(10)
    ])
    await session.commit()

    response = client.get(
        '/todos/?offset=2&limit=3',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_to_dos


@pytest.mark.asyncio
async def test_delet_to_do(token, user, session, client):
    todo = todo_factory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted'}


def test_delete_todo_error(client, token):
    response = client.delete(
        f'/todos/{10}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_todo_error_user(client, token, user, session, other_token):
    todo = todo_factory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {other_token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token):
    todo = todo_factory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'
