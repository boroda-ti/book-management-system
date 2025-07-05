import re

from pydantic import BaseModel, model_validator, field_validator


PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,64}$")


class UserCreateRequest(BaseModel):
    username: str
    password_1: str
    password_2: str


    @field_validator("password_1")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise ValueError("Password must contain at least 1 lowercase, 1 uppercase letter and 1 number, and be between 8 and 64 symbols long")
        
        return value


    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreateRequest":
        if self.password_1 != self.password_2:
            raise ValueError("Passwords do not match")
        
        return self


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserReadResponse(BaseModel):
    id: int
    username: str
    is_admin: bool