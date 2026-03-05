from pydantic import BaseModel, ConfigDict, EmailStr


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
    model_config = ConfigDict(from_attributes=True)


class UserDB(User):
    id: int


class ListUsers(BaseModel):
    users: list[UserPublic]
