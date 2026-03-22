from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_create_user_returns_ok(client, mock_db_time):
    response = client.post(
        '/Users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_read_users_with_users(client, user, token):
    userSchema = UserPublic.model_validate(user).model_dump()
    response = client.get('/Users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [userSchema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/Users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'alice', 'email': 'alice@gmail.com', 'password': '123321'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@gmail.com',
        'id': user.id,
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/Users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_get_user_by_id(client, user):
    response = client.get('/Users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_get_user_by_id_not_found(client):
    response = client.get('/Users/099')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found by id'}


def test_update_forbidden_error(client, user, token):
    another_user = client.post(
        '/Users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    ).json()

    response = client.put(
        f'/Users/{another_user["id"]}',
        headers={'Authorization': f'Bearer {token}'},  # ← Token do Bob (id=1)
        json={
            'username': 'alice_updated',
            'email': 'alice_updated@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_forbidden_error(client, other_user, token):

    response = client.delete(
        f'/Users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},  # ← Token do Bob (id=1)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_integrity_error(client, user, token):
    # Inserindo fausto
    client.post(
        '/Users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    # Alterando o user das fixture para fausto
    response_update = client.put(
        f'/Users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username already exists or Email already exists'
    }


def test_email_already_exist(client, user):
    response = client.post(
        '/Users/', json={'username': 'teste', 'email': user.email, 'password': 'senha'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_name_already_exist(client, user):
    response = client.post(
        '/Users/',
        json={
            'username': user.username,
            'email': 'testejunior@exemple.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}
