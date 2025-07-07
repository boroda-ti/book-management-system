from fastapi import APIRouter, HTTPException, Depends, Request

from app.limiter import limiter
from app.schemas import UserCreateRequest, UserLoginRequest, TokenResponse, UserReadResponse
from app.services import auth_service
from app.middleware import middleware_get_current_user


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserReadResponse)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreateRequest):
    try:
        created_user = await auth_service.create_user(user.username, user.password_1)
        return created_user
    
    except Exception:
        raise HTTPException(status_code=400, detail="User with this username already exists")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, user: UserLoginRequest):
    auth_user = await auth_service.authenticate_user(user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth_service.create_access_token(
        data={
            "sub": auth_user["username"],
            "id": auth_user["id"],
            "is_admin": auth_user["is_admin"]
        }
    )

    return {"access_token": token}


@router.get("/me", response_model=UserReadResponse)
@limiter.limit("5/minute")
async def get_current_user(request: Request, current_user: UserReadResponse = Depends(middleware_get_current_user)):
    return current_user