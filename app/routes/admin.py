from fastapi import APIRouter, HTTPException, Depends, Request

from app.limiter import limiter
from app.middleware import middleware_get_current_admin_user
from app.schemas import (
    AdminAuthorCreateRequest, AdminAuthorUpdateRequest,
    AdminGenreCreateRequest, AdminGenreUpdateRequest,
    AdminBookCreateRequest, AdminBookUpdateRequest,
    AuthorReadResponse, GenreReadResponse, BookReadResponse,
    UserReadResponse
)
from app.services import author_service, book_service, genre_service


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/author", response_model=AuthorReadResponse)
@limiter.limit("5/minute")
async def create_author(request: Request, author: AdminAuthorCreateRequest, 
                        current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        created_author = await author_service.create_author(author.name, author.user_id)
        if not created_author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        return author_service.generate_response(created_author)
    
    except KeyError:
        raise HTTPException(status_code=400, detail="Author already exists for this user or user with this id does not exist")

    except Exception:
        raise HTTPException(status_code=400, detail="Author creation failed")


@router.put("/author/{author_id}", response_model=AuthorReadResponse)
@limiter.limit("5/minute")
async def update_author(request: Request, author_id: int, author: AdminAuthorUpdateRequest, 
                        current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        updated_author = await author_service.update_author(author_id, author.name, author.user_id)
        if not updated_author:
            raise HTTPException(status_code=404, detail="Author not found")
        
        return author_service.generate_response(updated_author)
    
    except Exception:
        raise HTTPException(status_code=400, detail="Author update failed")


@router.delete("/author/{author_id}")
@limiter.limit("5/minute")
async def delete_author(request: Request, author_id: int, 
                        current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
        try:
            await author_service.delete_author(author_id)
            return {"success": True}

        except Exception:
            raise HTTPException(status_code=400, detail="Author deletion failed")


@router.post("/genre", response_model=GenreReadResponse)
@limiter.limit("5/minute")
async def create_genre(request: Request, genre: AdminGenreCreateRequest, 
                       current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        created_genre = await genre_service.create_genre(genre.name)
        if not created_genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        return created_genre

    except Exception:
        raise HTTPException(status_code=400, detail="Genre creation failed")


@router.put("/genre/{genre_id}", response_model=GenreReadResponse)
@limiter.limit("5/minute")
async def update_genre(request: Request, genre_id: int, genre: AdminGenreUpdateRequest, 
                       current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        updated_genre = await genre_service.update_genre(genre.name, genre_id)
        if not updated_genre:
            raise HTTPException(status_code=404, detail="Genre not found")

        return updated_genre

    except Exception:
        raise HTTPException(status_code=400, detail="Genre updating failed")


@router.delete("/genre/{genre_id}")
@limiter.limit("5/minute")
async def delete_genre(request: Request, genre_id: int, 
                       current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        await genre_service.delete_genre(genre_id)
        return {"success": True}

    except Exception:
        raise HTTPException(status_code=400, detail="Genre deletion failed")


@router.post("/books", response_model=BookReadResponse)
@limiter.limit("5/minute")
async def create_book(request: Request, book: AdminBookCreateRequest, 
                       current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        created_book = await book_service.create_book(
            title=book.title,
            genre_id=book.genre_id,
            published_year=book.published_year,
            author_ids=book.author_ids,
            created_by=book.created_by or current_user["id"]
        )
        if not created_book:
            raise HTTPException(status_code=404, detail="Book not found")

        return created_book

    except Exception:
        raise HTTPException(status_code=400, detail="Book creation failed")


@router.put("/books/{book_id}", response_model=BookReadResponse)
@limiter.limit("5/minute")
async def update_book(request: Request, book_id: int, book: AdminBookUpdateRequest, 
                       current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        updated_book = await book_service.update_book(
            book_id=book_id,
            title=book.title,
            genre_id=book.genre_id,
            published_year=book.published_year,
            author_ids=book.author_ids,
            created_by=book.created_by or current_user["id"]
        )
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")

        return updated_book

    except Exception:
        raise HTTPException(status_code=400, detail="Book update failed")


@router.delete("/books/{book_id}")
@limiter.limit("5/minute")
async def delete_book(request: Request, book_id: int,
                       current_user: UserReadResponse = Depends(middleware_get_current_admin_user)):
    try:
        await book_service.delete_book(book_id)
        return {"success": True}

    except Exception:
        raise HTTPException(status_code=400, detail="Book deletion failed")