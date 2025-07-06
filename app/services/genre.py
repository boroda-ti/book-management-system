from typing import Optional

from app.database import get_database
from app.utils import SingletonMeta


class GenreService(metaclass=SingletonMeta):

    async def select_genre(self) -> Optional[list]:
        async with get_database().get_pool().acquire() as conn:
            rows = await conn.fetch("SELECT * FROM genres")

            if rows:
                return [{
                    "id": row["id"],
                    "name": row["name"]
                } for row in rows]

            return None
        
    
    async def get_genre(self, genre_id: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM genres WHERE id = $1", genre_id)

            if row:
                return dict(row)


    async def create_genre(self, name: str) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            try:
                create_query = "INSERT INTO genres (name) VALUES ($1) RETURNING id, name"
                create_row = await conn.fetchrow(create_query, name)

            except Exception:
                raise ValueError("Genre creation failed")

            if create_row:
                return dict(create_row)

            return None


    async def update_genre(self, name: str, genre_id: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            try:
                update_query = "UPDATE genres SET name = $1 WHERE id = $2 RETURNING id, name"
                update_row = await conn.fetchrow(update_query, name, genre_id)

            except Exception:
                raise ValueError("Genre updating failed")

            if update_row:
                return dict(update_row)

            return None


    async def delete_genre(self, genre_id: int) -> bool:
        async with get_database().get_pool().acquire() as conn:
            try:
                await conn.execute("DELETE FROM genres WHERE id = $1", genre_id)

            except Exception:
                raise ValueError("Genre deletion failed")

            return True