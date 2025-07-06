from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request

from app.limiter import limiter
from app.middleware import middleware_get_current_user
from app.schemas import GenreReadResponse, GenreListResponse
from app.services import genre_service


router = APIRouter(prefix="/genre", tags=["Genre"])


@router.get("/", response_model=GenreListResponse)
@limiter.limit("5/minute")
async def get_genre(request: Request, current_user: dict = Depends(middleware_get_current_user)):
    genres = await genre_service.select_genre()

    if not genres:
        raise HTTPException(status_code=404, detail="No genres found")
    
    return GenreListResponse(genres=genres)


@router.get("/{genre_id}", response_model=GenreReadResponse)
@limiter.limit("5/minute")
async def get_genre(request: Request, genre_id: int, current_user: dict = Depends(middleware_get_current_user)):
    genre = await genre_service.get_genre(genre_id)

    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    return GenreReadResponse(id=genre["id"], name=genre["name"])