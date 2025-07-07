from typing import Optional
from pydantic import BaseModel, field_validator

from app.schemas.author import AuthorCreateUpdateRequest
from app.schemas.books import BookCreateRequest


class AdminAuthorCreateRequest(AuthorCreateUpdateRequest):
    user_id: Optional[int] = None

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("user_id must be a positive integer or None")
        return value
    

class AdminAuthorUpdateRequest(AdminAuthorCreateRequest):
    pass


class AdminGenreCreateRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 30:
            raise ValueError("name must be between 2 and 30 symbols long")
        return value
    

class AdminGenreUpdateRequest(AdminGenreCreateRequest):
    pass


class AdminBookCreateRequest(BookCreateRequest):
    created_by: Optional[int] = None

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("created_by must be a positive integer or None")
        return value
    

class AdminBookUpdateRequest(AdminBookCreateRequest):
    pass