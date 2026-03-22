import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from fastapi_zero.routers import auth, todo, user
from fastapi_zero.schemas import Message

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title='FastAPI ZERO')

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todo.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Hello World!'}
