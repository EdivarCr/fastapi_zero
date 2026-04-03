from fastapi_zero.core.security import create_access_token, verify_password
from fastapi_zero.exeptions import InvalidCredentialsError
from fastapi_zero.model.models import User as UserModel
from fastapi_zero.repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    async def authenticate(self, email: str, password: str) -> dict:
        user = await self.repo.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsError('Incorrect username or password')

        if not verify_password(password, user.password):
            raise InvalidCredentialsError('Icorrect password')

        access_token = create_access_token({'sub': user.email})
        return {'access_token': access_token, 'token_type': 'Bearer'}

    @staticmethod
    def refresh_token(user: UserModel) -> dict:
        new_access_token = create_access_token(data={'sub': user.email})
        return {'access_token': new_access_token, 'token_type': 'bearer'}
