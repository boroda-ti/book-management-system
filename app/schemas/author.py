from typing import Optional
from pydantic import BaseModel, field_validator

from app.schemas.auth import UserReadResponse


class AuthorCreateUpdateRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 60:
            raise ValueError("name must be between 2 and 60 symbols long")
        
        return value
    
    
class AuthorReadResponse(BaseModel):
    id: int
    name: str
    user: Optional[UserReadResponse] = None