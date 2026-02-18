from http import HTTPStatus


def test_read_root_html_retorna_ok(client):
    # client = TestClient(app)  # arrange
    response = client.get('/')  # act

    assert response.status_code == HTTPStatus.OK


def test_creat_user_retona_ok(client):

    response = client.post(
        '/Users/',
        json={'username': 'bob', 'password': '123', 'email': 'bob123@gmail.com'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'username': 'bob', 'email': 'bob123@gmail.com'}


def test_read_users(client):
    response = client.get('/Users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'id': 1, 'username': 'bob', 'email': 'bob123@gmail.com'}]
    }


def test_udpate_user(client):
    response = client.put(
        '/Users/1',
        json={'username': 'alice', 'email': 'alice@gmail.com', 'password': '123321'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'username': 'alice', 'email': 'alice@gmail.com', 'id': 1}

    response = client.put(
        '/Users/-1',
        json={'username': 'teste', 'email': 'test@gmail.com', 'password': 'teste'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client):
    response = client.delete('/Users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'username': 'alice', 'email': 'alice@gmail.com', 'id': 1}

    response = client.delete('/Users/-1')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
