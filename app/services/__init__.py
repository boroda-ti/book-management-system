from .auth import AuthService
from .author import AuthorService

auth_service = AuthService()
author_service = AuthorService()

__all__ = ["auth_service", "AuthService",
           "author_service"]