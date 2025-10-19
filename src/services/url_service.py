"""URL shortening service."""

import random
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.url import URL
from src.schemas.url import URLCreate


class URLService:
    """Service for URL shortening operations."""

    @staticmethod
    def generate_short_code(length: int = settings.SHORT_URL_LENGTH) -> str:
        """Generate a random short code."""
        characters = string.ascii_letters + string.digits
        return "".join(random.choices(characters, k=length))

    @staticmethod
    async def create_short_url(
        db: AsyncSession, url_create: URLCreate
    ) -> URL:
        """Create a new shortened URL."""
        # Use custom code if provided, otherwise generate one
        if url_create.custom_code:
            short_code = url_create.custom_code
            # Check if custom code already exists
            existing = await db.execute(
                select(URL).where(URL.short_code == short_code)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Short code '{short_code}' is already taken")
        else:
            # Generate unique short code
            max_attempts = 10
            for _ in range(max_attempts):
                short_code = URLService.generate_short_code()
                existing = await db.execute(
                    select(URL).where(URL.short_code == short_code)
                )
                if not existing.scalar_one_or_none():
                    break
            else:
                raise RuntimeError("Could not generate unique short code")

        # Create new URL entry
        db_url = URL(
            original_url=str(url_create.url),
            short_code=short_code,
        )
        db.add(db_url)
        await db.flush()
        await db.refresh(db_url)
        return db_url

    @staticmethod
    async def get_url_by_short_code(db: AsyncSession, short_code: str) -> URL | None:
        """Get URL by short code."""
        result = await db.execute(select(URL).where(URL.short_code == short_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def increment_click_count(db: AsyncSession, url: URL) -> None:
        """Increment the click count for a URL."""
        url.clicks += 1
        await db.flush()

    @staticmethod
    async def get_all_urls(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[URL]:
        """Get all URLs with pagination."""
        result = await db.execute(select(URL).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def delete_url(db: AsyncSession, short_code: str) -> bool:
        """Delete a URL by short code."""
        url = await URLService.get_url_by_short_code(db, short_code)
        if url:
            await db.delete(url)
            await db.flush()
            return True
        return False
