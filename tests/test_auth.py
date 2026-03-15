from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': user.clean_password}
    )

    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_get_token_not_user_error(client, user):
    bug_name = 'naoexiste@gmail.com'
    response = client.post(
        '/auth/token', data={'username': bug_name, 'password': user.password}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_get_token_not_password_error(client, user):
    bug_password = 'naotemsenha'
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': bug_password}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Icorrect password'}
