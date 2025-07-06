import json, csv, io
from typing import Optional, Iterator

from app.database import get_database
from app.utils import SingletonMeta


class BookService(metaclass=SingletonMeta):
    async def create_book(self, title: str, genre_id: Optional[int], published_year: int, author_ids: list[int], created_by: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    """
                    INSERT INTO books (title, genre_id, published_year, created_by)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id, title, genre_id, published_year, created_by, created_at, updated_at
                    """,
                    title, genre_id, published_year, created_by
                )

                book_id = row["id"]

                try:
                    for author_id in author_ids:
                        await conn.execute(
                            "INSERT INTO book_authors (book_id, author_id) VALUES ($1, $2)",
                            book_id, author_id
                        )

                except Exception:
                    raise ValueError("Author does not exist")

        return await self.get_book(book_id)


    async def get_book(self, book_id: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            book = await conn.fetchrow("SELECT * FROM books WHERE id = $1", book_id)
            if not book:
                return None
            
            author_rows = await conn.fetch(
                """
                SELECT a.id, a.name, 
                    u.id as user_id, u.username, u.is_admin
                FROM authors a
                JOIN book_authors ba ON a.id = ba.author_id
                LEFT JOIN users u ON a.user_id = u.id
                WHERE ba.book_id = $1
                """,
                book_id
            )

            return self.generate_response(dict(book), list(author_rows))


    async def list_books(self, page: int, limit: int, sort_by: str, sort_order: str,
                         title: Optional[str], author_name: Optional[str], genre_id: Optional[int],
                         year_from: Optional[int], year_to: Optional[int]) -> Optional[list[dict]]:
        async with get_database().get_pool().acquire() as conn:
            offset = (page - 1) * limit
            sort_map = {
                "id": "b.id",
                "title": "b.title",
                "year": "b.published_year",
                "author": "a.name"
            }
            order_field = sort_map.get(sort_by, "b.title")
            order_dir = "DESC" if sort_order.lower() == "desc" else "ASC"

            filters = []
            params = []

            if title:
                filters.append("b.title ILIKE $%d" % (len(params) + 1))
                params.append(f"%{title}%")
            if author_name:
                filters.append("a.name ILIKE $%d" % (len(params) + 1))
                params.append(f"%{author_name}%")
            if genre_id:
                filters.append("b.genre_id = $%d" % (len(params) + 1))
                params.append(genre_id)
            if year_from:
                filters.append("b.published_year >= $%d" % (len(params) + 1))
                params.append(year_from)
            if year_to:
                filters.append("b.published_year <= $%d" % (len(params) + 1))
                params.append(year_to)

            filter_sql = " AND ".join(filters)
            if filter_sql:
                filter_sql = "WHERE " + filter_sql

            query = f"""
                SELECT
                    b.id, b.title, b.genre_id, b.published_year,
                    b.created_by, b.created_at, b.updated_at,
                    a.id AS author_id, a.name AS author_name,
                    u.id as user_id, u.username, u.is_admin
                FROM books b
                LEFT JOIN book_authors ba ON b.id = ba.book_id
                LEFT JOIN authors a ON a.id = ba.author_id
                LEFT JOIN users u ON a.user_id = u.id
                {filter_sql}
                ORDER BY {order_field} {order_dir}
                LIMIT ${len(params)+1} OFFSET ${len(params)+2}
            """

            params.extend([limit, offset])
            rows = await conn.fetch(query, *params)

            books_dict = {}
            for row in rows:
                book_id = row["id"]
                if book_id not in books_dict:
                    books_dict[book_id] = {
                        "id": book_id,
                        "title": row["title"],
                        "genre_id": row["genre_id"],
                        "published_year": row["published_year"],
                        "created_by": row["created_by"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "authors": []
                    }
                if row["author_id"]:
                    books_dict[book_id]["authors"].append({
                        "id": row["author_id"], 
                        "name": row["author_name"],
                        "user": {
                            "id": row["user_id"],
                            "username": row["username"],
                            "is_admin": row["is_admin"]
                        } if row["user_id"] else None
                    })

            return list(books_dict.values()) or None


    async def update_book(self, book_id: int, title: str, genre_id: Optional[int], published_year: int, 
                          author_ids: list[int], created_by: Optional[int] = None) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            async with conn.transaction():
                try:
                    if created_by:
                        await conn.fetchrow(
                            """
                            UPDATE books SET title = $1, genre_id = $2, published_year = $3, created_by = $4
                            WHERE id = $5
                            RETURNING id, title, genre_id, published_year, created_at, updated_at
                            """,
                            title, genre_id, published_year, created_by, book_id
                        )
                        
                    else:
                        await conn.fetchrow(
                            """
                            UPDATE books SET title = $1, genre_id = $2, published_year = $3
                            WHERE id = $4
                            RETURNING id, title, genre_id, published_year, created_at, updated_at
                            """,
                            title, genre_id, published_year, book_id
                        )
                
                except Exception:
                    raise ValueError("Book update failed")

                await conn.execute("DELETE FROM book_authors WHERE book_id = $1", book_id)

                try:
                    for author_id in author_ids:
                        await conn.execute(
                            "INSERT INTO book_authors (book_id, author_id) VALUES ($1, $2)",
                            book_id, author_id
                        )

                except Exception:
                    raise ValueError("Author does not exist")

        return await self.get_book(book_id)


    async def delete_book(self, book_id: int) -> bool:
        async with get_database().get_pool().acquire() as conn:
            try:
                await conn.execute("DELETE FROM books WHERE id = $1", book_id)

            except Exception:
                raise ValueError("Book deletion failed")

            return True


    async def get_user_author(self, user_id: int) -> Optional[dict]:
        async with get_database().get_pool().acquire() as conn:
            row = await conn.fetchrow("SELECT id, name FROM authors WHERE user_id = $1", user_id)
            if not row:
                return None
            
            return dict(row)


    async def check_book_creator(self, book_id: int, user_id: int) -> bool:
        async with get_database().get_pool().acquire() as conn:
            row = await conn.fetchrow("SELECT created_by FROM books WHERE id = $1", book_id)
            if not row:
                return False
            
            return row["created_by"] == user_id


    def generate_response(self, book: dict, authors: list) -> dict:
        return {
            "id": book["id"],
            "title": book["title"],
            "genre_id": book.get("genre_id"),
            "published_year": book["published_year"],
            "authors": [
                {
                    "id": author["id"], 
                    "name": author["name"], 
                    "user": {
                        "id": author["user_id"],
                        "username": author["username"],
                        "is_admin": author["is_admin"]
                    } if author["user_id"] else None
                } for author in authors
            ],
            "created_at": book["created_at"],
            "updated_at": book["updated_at"]
        }
    

    def parse_json_file(self, content: bytes, author_id: int) -> Optional[list[dict]]:
        data = json.loads(content.decode('utf-8'))

        for book in data:
            if not isinstance(book, dict):
                return [{"title": None, "error": "Invalid book format in JSON file"}]
            
            if author_id not in book.get("author_ids", []):
                return [{"title": book.get("title", None), "error": "Author must be one of the authors of the book"}]
            
        return data


    def parse_csv_file(self, content: bytes, author_id: int) -> Optional[list[dict]]:
        text = content.decode("utf-8").splitlines()
        reader = csv.DictReader(text)
        data = []

        for row in reader:
            try:
                authors_id = json.loads(row["author_ids"])

            except Exception:
                return [{"title": row.get("title", None), "error": "Invalid author_ids format in CSV file"}]
            
            if author_id not in authors_id:
                return [{"title": row.get("title", None), "error": "Author must be one of the authors of the book"}]
            
            if not row["title"] or not row["published_year"]:
                return [{"title": row.get("title", None), "error": "Title and published_year are required"}]
            
            data.append({
                "title": row["title"],
                "genre_id": int(row["genre_id"]) if row["genre_id"] else None,
                "published_year": int(row["published_year"]),
                "author_ids": authors_id
            })

        return data
    

    def serialize_export_json(self, books: list[dict]) -> list:
        output = []

        for book in books:
            output.append({
                "id": book["id"],
                "title": book["title"],
                "genre_id": book.get("genre_id"),
                "published_year": book["published_year"],
                "authors": [a["name"] for a in book.get("authors", [])],
                "created_at": book["created_at"].isoformat(),
                "updated_at": book["updated_at"].isoformat()
            })

        return output


    def generate_export_csv(self, books: list[dict]) -> Iterator[str]:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "title", "genre_id", "published_year", "authors", "created_at", "updated_at"])

        for book in books:
            writer.writerow([
                book["id"],
                book["title"],
                book.get("genre_id"),
                book["published_year"],
                "; ".join([a["name"] for a in book.get("authors", [])]),
                book["created_at"].isoformat(),
                book["updated_at"].isoformat()
            ])

        output.seek(0)
        return iter([output.getvalue()])