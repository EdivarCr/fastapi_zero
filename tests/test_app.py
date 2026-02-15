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


