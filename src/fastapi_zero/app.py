from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_section

from .models import User as UserModel
from .schemas import ListUsers, Message, User, UserPublic

app = FastAPI(title='FastAPI ZERO')

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}


@app.post('/Users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: User, session: Session = Depends(get_section)):

    db_user = session.scalar(
        select(UserModel).where(
            (UserModel.username == user.username) | (UserModel.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = UserModel(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/Users/', status_code=HTTPStatus.OK, response_model=ListUsers)
def get_users(limit=10, offset=0, session=Depends(get_section)):
    users = session.scalars(select(UserModel).limit(limit).offset(offset))
    return {'users': list(users)}


@app.put('/Users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int, user: User, session=Depends(get_section)):
    user_db = session.scalar(select(UserModel).where(UserModel.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    try:
        user_db.username = user.username
        user_db.email = user.email
        user_db.password = user.password

        session.add(user_db)
        session.commit()

        return user_db
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username already exists or Email already exists',
        )


@app.delete('/Users/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int, session=Depends(get_section)):
    user_db = session.scalar(select(UserModel).where(UserModel.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    session.delete(user_db)
    session.commit()

    return {'message': 'User deleted'}
