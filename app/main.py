from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routes import auth
from app.routes import author
from app.routes import books
from app.database import get_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(author.router)
app.include_router(books.router)