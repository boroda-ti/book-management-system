from typing import Optional

from app.database import get_database
from app.utils import SingletonMeta


class AuthorService(metaclass=SingletonMeta):

    def __init__(self):
        self.select_author_query = """
        SELECT a.id AS author_id, a.name AS author_name,
        u.id AS user_id, u.username, u.is_admin
        FROM authors a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.id = $1
        """

    async def create_author(self, name: str, user_id: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            try:
                insert_query = "INSERT INTO authors (name, user_id) VALUES ($1, $2) RETURNING id, name, user_id"
                insert_row = await conn.fetchrow(insert_query, name, user_id)

            except Exception:
                raise KeyError("Author already exists for this user")

            author_id = insert_row.get('id')
            if not insert_row or not author_id:
                raise ValueError("Author creation failed")
            
            row = await conn.fetchrow(self.select_author_query, author_id)

            if row:
                return dict(row)
            
            return None
        

    async def update_author(self, author_id: int, name: str) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            update_query = "UPDATE authors SET name = $1 WHERE id = $2 RETURNING id, name, user_id"
            update_row = await conn.fetchrow(update_query, name, author_id)

            author_id = update_row.get('id')

            if not update_row or not author_id:
                raise ValueError("Author update failed")
            
            row = await conn.fetchrow(self.select_author_query, author_id)

            if row:
                return dict(row)
            
            return None
        

    async def select_author(self, author_id: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            row = await conn.fetchrow(self.select_author_query, author_id)

            if row:
                return dict(row)
            
            return None
        
    
    def generate_response(self, author: dict) -> dict:
        return {
            "id": author["author_id"],
            "name": author["author_name"],
            "user": {
                "id": author["user_id"],
                "username": author["username"],
                "is_admin": author["is_admin"]
            }
        }