from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import create_access_token, settings


def test_create_access_token():
    data = {'teste': 'teste'}
    token = create_access_token(data)

    decoded_token = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded_token['teste'] == data['teste']

    assert 'exp' in decoded_token


def test_user_email_error(client):

    invalid_token = create_access_token({'sub': 'emailinvalido@example.com'})

    response = client.put(
        '/Users/1',
        headers={'Authorization': f'Bearer {invalid_token}'},
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_subject_email_error(client):

    invalid_token = create_access_token({'sub': ''})

    response = client.put(
        '/Users/1',
        headers={'Authorization': f'Bearer {invalid_token}'},
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_decode_error(client, user, token):
    response = client.delete(
        f'/Users/{user.id}',
        headers={'Authorization': f'Bearer {""}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
