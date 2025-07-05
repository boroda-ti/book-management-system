import asyncpg
from typing import Optional

from app.config import BaseConfig
from app.utils import SingletonMeta


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if not self._pool:
            if BaseConfig.get("TESTING") == 1:
                dsn = f"postgresql://{BaseConfig.get('DB_USER_TEST')}:{BaseConfig.get('DB_PASSWORD_TEST')}@{BaseConfig.get('DB_HOST_TEST')}:{BaseConfig.get('DB_PORT_TEST')}/{BaseConfig.get('DB_NAME_TEST')}"

            else:
                dsn = f"postgresql://{BaseConfig.get('DB_USER')}:{BaseConfig.get('DB_PASSWORD')}@{BaseConfig.get('DB_HOST')}:{BaseConfig.get('DB_PORT')}/{BaseConfig.get('DB_NAME')}"

            self._pool = await asyncpg.create_pool(dsn=dsn)

    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    def get_pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("Database not initialized.")
        return self._pool
    
    
_db_instance: Optional[Database] = None

def get_database() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance