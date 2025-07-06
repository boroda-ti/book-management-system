from .auth import AuthService
from .author import AuthorService
from .books import BookService
from .genre import GenreService


auth_service = AuthService()
author_service = AuthorService()
book_service = BookService()
genre_service = GenreService()


__all__ = ["auth_service", "AuthService",
           "author_service", "book_service", "genre_service"]