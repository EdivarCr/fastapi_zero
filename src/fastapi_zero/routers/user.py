from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.core.database import get_section
from fastapi_zero.core.security import get_current_user
from fastapi_zero.exeptions import (
    ForbiddenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from fastapi_zero.model.models import User as UserModel
from fastapi_zero.repository import UserRepository
from fastapi_zero.schemas.schemas import ListUsers, Message, User, UserPublic
from fastapi_zero.services import UserService

router = APIRouter(prefix='/Users', tags=['users'])

Session = Annotated[AsyncSession, Depends(get_section)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]


def get_user_service(session: Session) -> UserService:
    return UserService(UserRepository(session))


UserSvc = Annotated[UserService, Depends(get_user_service)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: User, service: UserSvc):
    try:
        return await service.create(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))


@router.get('/', status_code=HTTPStatus.OK, response_model=ListUsers)
async def get_users(
    service: UserSvc, current_user: CurrentUser, limit: int = 10, offset: int = 0
):
    users = await service.list(limit=limit, offset=offset)
    return {'users': list(users)}


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int, user: User, service: UserSvc, current_user: CurrentUser
):
    try:
        return await service.update(user_id, current_user, user)
    except ForbiddenError as e:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username already exists or Email already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(user_id: int, service: UserSvc, current_user: CurrentUser):
    try:
        await service.delete(user_id, current_user)
        return {'message': 'User deleted'}
    except ForbiddenError as e:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=str(e))


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user_by_id(user_id: int, service: UserSvc):
    try:
        return await service.get(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
