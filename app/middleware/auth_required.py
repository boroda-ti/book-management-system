from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def middleware_get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = AuthService.decode_access_token(token)
    user_id: int = payload.get("id")
    username: str = payload.get("sub")
    is_admin: bool = payload.get("is_admin", False)

    if user_id is None or username is None:
        raise credentials_exception
    
    return {"id": user_id, "username": username, "is_admin": is_admin}
