import os
os.environ["TESTING"] = "1"

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import get_database


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    db = get_database()
    await db.connect()
    yield
    await db.disconnect()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def clear_tables():
    yield
    db = get_database()
    await db.connect()
    async with db.get_pool().acquire() as conn:
        await conn.execute("TRUNCATE users RESTART IDENTITY CASCADE;")


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as aclient:
        yield aclient