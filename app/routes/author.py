from fastapi import APIRouter, HTTPException, Depends, Request

from app.limiter import limiter
from app.middleware import middleware_get_current_user
from app.schemas import AuthorCreateUpdateRequest, AuthorReadResponse
from app.services import author_service


router = APIRouter(prefix="/author", tags=["Author"])


@router.post("/create", response_model=AuthorReadResponse)
@limiter.limit("5/minute")
async def create_author(request: Request, author: AuthorCreateUpdateRequest, current_user: dict = Depends(middleware_get_current_user)):
    
    try:
        created_author = await author_service.create_author(author.name, current_user["id"])
        if not created_author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        return author_service.generate_response(created_author)
    
    except KeyError:
        raise HTTPException(status_code=400, detail="Author already exists for this user")

    except Exception:
        raise HTTPException(status_code=400, detail="Author creation failed")


@router.get("/{author_id}", response_model=AuthorReadResponse)
@limiter.limit("5/minute")
async def get_author(request: Request, author_id: int, current_user: dict = Depends(middleware_get_current_user)):

    author = await author_service.select_author(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return author_service.generate_response(author)


@router.patch("/{author_id}", response_model=AuthorReadResponse)
@limiter.limit("5/minute")
async def update_author(request: Request, author_id: int, author: AuthorCreateUpdateRequest, current_user: dict = Depends(middleware_get_current_user)):
    
    try:
        updated_author = await author_service.update_author(author_id, author.name)
        if not updated_author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        return author_service.generate_response(updated_author)
    
    except Exception:
        raise HTTPException(status_code=400, detail="Author update failed")