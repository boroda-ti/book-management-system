from typing import Optional, List
from pydantic import BaseModel


class GenreReadResponse(BaseModel):
    id: int
    name: str


class GenreListResponse(BaseModel):
    genres: Optional[List[GenreReadResponse]]