from http import HTTPStatus
from fastapi.testclient import TestClient
from fastapi_zero.app import app



def test_read_root_retorna_ok():
    client  = TestClient(app) # arrange (preparação)
    response = client.get('/') # act (ação)

    assert response.status_code == HTTPStatus.OK # assert (verificação)
    assert response.json() == {'message': 'Hello World'}
                           