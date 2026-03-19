from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_zero.models import TodoState


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


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 10


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int


class TodoList(BaseModel):
    todos: list[TodoPublic]


class FilterTodo(FilterPage):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
