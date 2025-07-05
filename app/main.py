from contextlib import asynccontextmanager
from fastapi import FastAPI

from app import database
from app.routes import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)