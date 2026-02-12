from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .schemas import Message, User, UserPublic




app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_root():
    return """
        <html>
            <head>
                <title> Ola  </title>
            </head>
            <body>
                <h1> oi </h1>
                <h2> oioi </h2>
            </body>
        </html> """

@app.get('/', status_code=HTTPStatus.OK, response_model=Message)

@app.post('/Users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: User):
    return user