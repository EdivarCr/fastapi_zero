from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int


class UserDB(User):
    id: int


class ListUsers(BaseModel):
    users: list[UserPublic]
