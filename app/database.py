import asyncpg
from typing import Optional

from app.config import BaseConfig
from app.utils import SingletonMeta


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(dsn=f"postgresql://{BaseConfig.get('DB_USER')}:{BaseConfig.get('DB_PASSWORD')}@{BaseConfig.get('DB_HOST')}:{BaseConfig.get('DB_PORT')}/{BaseConfig.get('DB_NAME')}",)

    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    def get_pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("Database not initialized.")
        return self._pool