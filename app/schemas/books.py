from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, field_validator, Field

from app.schemas.author import AuthorReadResponse


class BookCreateRequest(BaseModel):
    title: str = Field(..., max_length=150)
    genre_id: Optional[int]
    published_year: int
    author_ids: List[int]

    @field_validator("published_year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        if not (1800 <= value <= date.today().year):
            raise ValueError("Published year must be between 1800 and current year")
        
        return value


class BookUpdateRequest(BookCreateRequest):
    pass


class BookReadResponse(BaseModel):
    id: int
    title: str
    genre_id: Optional[int]
    published_year: int
    authors: List[AuthorReadResponse]
    created_at: datetime
    updated_at: datetime


class BookListResponse(BaseModel):
    books: Optional[List[BookReadResponse]]
    total: int
    page: int
    limit: int


class BookDeleteResponse(BaseModel):
    success: bool