from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.middleware import middleware_get_current_user
from app.schemas import BookCreateRequest, BookUpdateRequest, BookReadResponse, BookListResponse, BookDeleteResponse
from app.services import book_service


router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/create", response_model=BookReadResponse)
async def create_book(book: BookCreateRequest, current_user: dict = Depends(middleware_get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    author = await book_service.get_user_author(current_user["id"])
    if not author:
        raise HTTPException(status_code=404, detail="Author not found for the current user")

    if author["id"] not in book.author_ids:
        raise HTTPException(status_code=409, detail="Author must be one of the authors of the book")

    try:
        created_book = await book_service.create_book(
            title=book.title,
            genre_id=book.genre_id,
            published_year=book.published_year,
            author_ids=book.author_ids,
            created_by=current_user["id"]
        )
        if not created_book:
            raise HTTPException(status_code=400, detail="Book not found")

        return created_book

    except Exception:
        raise HTTPException(status_code=400, detail="Book creation failed")
    

@router.get("/{book_id}", response_model=BookReadResponse)
async def get_book(book_id: int, current_user: dict = Depends(middleware_get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    book = await book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.get("/", response_model=BookListResponse)
async def list_books(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    title: Optional[str] = Query(None),
    author_name: Optional[str] = Query(None),
    genre_id: Optional[int] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    current_user: dict = Depends(middleware_get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    books = await book_service.list_books(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        title=title,
        author_name=author_name,
        genre_id=genre_id,
        year_from=year_from,
        year_to=year_to
    )
    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return BookListResponse(books=books, total=len(books), page=page, limit=limit)


@router.put("/{book_id}", response_model=BookReadResponse)
async def update_book(book_id: int, book: BookUpdateRequest, current_user: dict = Depends(middleware_get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    is_creator = await book_service.check_book_creator(book_id, current_user["id"])
    if not is_creator:
        raise HTTPException(status_code=406, detail="Only the creator can update the book")

    author = await book_service.get_user_author(current_user["id"])
    if not author:
        raise HTTPException(status_code=404, detail="Author not found for the current user")

    if author["id"] not in book.author_ids:
        raise HTTPException(status_code=409, detail="Author must be one of the authors of the book")

    try:
        updated_book = await book_service.update_book(
            book_id=book_id,
            title=book.title,
            genre_id=book.genre_id,
            published_year=book.published_year,
            author_ids=book.author_ids
        )
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")

        return updated_book

    except Exception:
        raise HTTPException(status_code=400, detail="Book update failed")
    

@router.delete("/{book_id}", response_model=BookDeleteResponse)
async def delete_book(book_id: int, current_user: dict = Depends(middleware_get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    is_creator = await book_service.check_book_creator(book_id, current_user["id"])
    if not is_creator:
        raise HTTPException(status_code=406, detail="Only the creator can update the book")

    try:
        await book_service.delete_book(book_id)
        return BookDeleteResponse(success=True)

    except Exception:
        raise HTTPException(status_code=400, detail="Book deletion failed")