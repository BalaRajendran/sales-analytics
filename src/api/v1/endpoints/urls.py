"""URL endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.exceptions import ConflictError, InternalServerError, NotFoundError
from src.schemas.common import ApiResponse
from src.schemas.url import URLCreate, URLResponse, URLStats
from src.services.url_service import URLService

router = APIRouter()


@router.post("/", response_model=ApiResponse[URLResponse], status_code=status.HTTP_201_CREATED)
async def create_short_url(
    url_create: URLCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new shortened URL.

    - **url**: The original URL to shorten
    - **custom_code**: Optional custom short code (must be unique)
    - **tags**: Optional tags for categorizing the URL
    """
    try:
        url = await URLService.create_short_url(db, url_create)
        url_response = URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"{settings.BASE_URL}/{url.short_code}",
            clicks=url.clicks,
            created_at=url.created_at,
        )
        return ApiResponse.success_response(url_response)
    except ValueError as e:
        # Handle duplicate short code or validation errors
        error_msg = str(e)
        if "already taken" in error_msg or "duplicate" in error_msg.lower():
            raise ConflictError(message=error_msg) from e
        raise InternalServerError(message=error_msg) from e
    except RuntimeError as e:
        raise InternalServerError(message=str(e)) from e


@router.get("/", response_model=ApiResponse[list[URLResponse]])
async def list_urls(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    List all shortened URLs with pagination.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    urls = await URLService.get_all_urls(db, skip=skip, limit=limit)
    url_list = [
        URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"{settings.BASE_URL}/{url.short_code}",
            clicks=url.clicks,
            created_at=url.created_at,
        )
        for url in urls
    ]
    return ApiResponse.success_response(url_list)


@router.get("/{short_code}/stats", response_model=ApiResponse[URLStats])
async def get_url_stats(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics for a shortened URL.

    - **short_code**: The short code to get statistics for
    """
    url = await URLService.get_url_by_short_code(db, short_code)
    if not url:
        raise NotFoundError(message=f"Short URL '{short_code}' not found")

    url_stats = URLStats(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        clicks=url.clicks,
        created_at=url.created_at,
        updated_at=url.updated_at,
    )
    return ApiResponse.success_response(url_stats)


@router.delete("/{short_code}", response_model=ApiResponse[dict])
async def delete_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a shortened URL.

    - **short_code**: The short code to delete
    """
    deleted = await URLService.delete_url(db, short_code)
    if not deleted:
        raise NotFoundError(message=f"Short URL '{short_code}' not found")

    return ApiResponse.success_response({"message": f"URL '{short_code}' deleted successfully"})


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Redirect to the original URL and increment click count.

    Note: This endpoint returns a redirect response, not the standard API response format.

    - **short_code**: The short code to redirect
    """
    url = await URLService.get_url_by_short_code(db, short_code)
    if not url:
        raise NotFoundError(message=f"Short URL '{short_code}' not found")

    # Increment click count
    await URLService.increment_click_count(db, url)
    await db.commit()

    # Redirect to original URL
    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
