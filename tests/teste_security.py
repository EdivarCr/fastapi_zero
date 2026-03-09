from jwt import decode

from fastapi_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_create_access_token():
    data = {'teste': 'teste'}
    token = create_access_token(data)

    decoded_token = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded_token['teste'] == data['teste']

    assert 'exp' in decoded_token
