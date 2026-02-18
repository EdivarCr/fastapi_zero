from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .schemas import ListUsers, Message, User, UserDB, UserPublic

app = FastAPI(title='FastAPI ZERO')

database = []


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
    user_db = UserDB(**user.model_dump(), id=len(database) + 1)

    database.append(user_db)
    return user_db


@app.get('/Users/', status_code=HTTPStatus.OK, response_model=ListUsers)
def get_users():
    return {'users': database}


@app.put('/Users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int, user: User):
    user_db_id = UserDB(**user.model_dump(), id=len(database))

    if user_id < 1 or user_id > len(database):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    database[user_id - 1] = user_db_id
    return user_db_id


@app.delete('/Users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    return database.pop(user_id - 1)
