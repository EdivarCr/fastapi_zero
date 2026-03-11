from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_read_root_html_retorna_ok(client):
    # client = TestClient(app)  # arrange
    response = client.get('/')  # act

    assert response.status_code == HTTPStatus.OK


def test_create_user_returns_ok(client):

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


def test_get_token(client, user):
    response = client.post(
        '/token', data={'username': user.email, 'password': user.clean_password}
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_get_token_not_user_error(client, user):
    bug_name = 'naoexiste@gmail.com'
    response = client.post(
        '/token', data={'username': bug_name, 'password': user.password}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_get_token_not_password_error(client, user):
    bug_password = 'naotemsenha'
    response = client.post(
        '/token', data={'username': user.email, 'password': bug_password}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Icorrect password'}


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


def test_delete_forbidden_error(client, token):
    another_user = client.post(
        '/Users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    ).json()

    response = client.delete(
        f'/Users/{another_user["id"]}',
        headers={'Authorization': f'Bearer {token}'},  # ← Token do Bob (id=1)
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
