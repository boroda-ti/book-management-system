from typing import Optional
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

from app import BaseConfig, database
from app.utils import SingletonMeta


class AuthService(metaclass=SingletonMeta):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)


    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)


    async def create_user(self, username: str, password: str) -> dict:
        async with database.get_pool().acquire() as conn:
            hashed_password = self.hash_password(password)
            query = "INSERT INTO users (username, password) VALUES ($1, $2) RETURNING id, username, is_admin"
            row = await conn.fetchrow(query, username, hashed_password)

            if row:
                return dict(row)
                
            else:
                raise ValueError("User creation failed")


    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        async with database.get_pool().acquire() as conn:
            query = "SELECT id, username, password, is_admin FROM users WHERE username = $1"
            row = await conn.fetchrow(query, username)

            if row and self.verify_password(password, row['password']):
                return dict(row)
            
            return None
        

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(BaseConfig.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))))
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, BaseConfig.get("JWT_SECRET_KEY"), algorithm=BaseConfig.get("JWT_ALGORITHM"))
    

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, BaseConfig.get("JWT_SECRET_KEY"), algorithms=[BaseConfig.get("JWT_ALGORITHM")])
            return payload
        
        except JWTError:
            return {}