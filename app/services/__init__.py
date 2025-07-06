from .auth import AuthService
from .author import AuthorService
from .books import BookService

auth_service = AuthService()
author_service = AuthorService()
book_service = BookService()

__all__ = ["auth_service", "AuthService",
           "author_service", "book_service"]