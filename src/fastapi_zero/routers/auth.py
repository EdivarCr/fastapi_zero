from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.core.database import get_section
from fastapi_zero.core.security import get_current_user
from fastapi_zero.exeptions import InvalidCredentialsError
from fastapi_zero.model.models import User as UserModel
from fastapi_zero.repository import AuthRepository
from fastapi_zero.schemas.schemas import Token
from fastapi_zero.services import AuthService

router = APIRouter(prefix='/auth', tags=['token'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[AsyncSession, Depends(get_section)]
Current_user = Annotated[UserModel, Depends(get_current_user)]


def get_auth_service(session: Session) -> AuthService:
    return AuthService(AuthRepository(session))


AuthSvc = Annotated[AuthService, Depends(get_auth_service)]


@router.post('/token', response_model=Token)
async def login_for_acess_token(form_data: OAuth2Form, service: AuthSvc):
    try:
        return await service.authenticate(form_data.username, form_data.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: Current_user, service: AuthSvc):
    return service.refresh_token(user)
