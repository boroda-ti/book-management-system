from fastapi import Depends, HTTPException

from app.middleware.auth_required import middleware_get_current_user
from app.schemas import UserReadResponse

def middleware_get_current_admin_user(current_user: UserReadResponse = Depends(middleware_get_current_user)) -> UserReadResponse:
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user