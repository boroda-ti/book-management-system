from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from app.database import get_database
from app.limiter import limiter
from app.routes import auth, author, books, genre, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    await db.connect()
    yield
    await db.disconnect()
    

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(auth.router)
app.include_router(author.router)
app.include_router(books.router)
app.include_router(genre.router)
app.include_router(admin.router)