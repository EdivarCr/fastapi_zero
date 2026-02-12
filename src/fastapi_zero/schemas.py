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