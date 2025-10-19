"""URL schemas with enhanced validation."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from src.schemas.common import BaseSchema, TimestampMixin
from src.schemas.validation import (
    DEFAULT_SHORT_CODE_RULES,
    validate_custom_code,
    validate_url_safety,
)


class URLCreate(BaseSchema):
    """Schema for creating a new shortened URL with enhanced validation."""

    url: HttpUrl = Field(
        ...,
        description="The original URL to shorten",
        examples=["https://example.com", "https://www.example.com/page"],
    )
    custom_code: str | None = Field(
        None,
        min_length=4,
        max_length=10,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Optional custom short code (4-10 characters, alphanumeric, hyphens, underscores)",
        examples=["mylink", "summer2024"],
    )
    tags: list[str] | None = Field(
        None,
        max_length=10,
        description="Optional tags for categorizing URLs",
        examples=[["marketing", "campaign"]],
    )

    @field_validator("url")
    @classmethod
    def validate_url_safety_check(cls, v: HttpUrl) -> HttpUrl:
        """Validate URL for safety concerns."""
        url_str = str(v)

        # Check URL safety
        is_safe, error_msg = validate_url_safety(url_str)
        if not is_safe:
            raise ValueError(f"URL validation failed: {error_msg}")

        # Check URL length
        if len(url_str) > 2048:
            raise ValueError("URL is too long (maximum 2048 characters)")

        return v

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code_rules(cls, v: str | None) -> str | None:
        """Validate custom code against rules."""
        if v is None:
            return v

        # Apply validation rules
        is_valid, error_msg = validate_custom_code(v, DEFAULT_SHORT_CODE_RULES)
        if not is_valid:
            raise ValueError(error_msg)

        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags."""
        if v is None:
            return v

        # Check each tag
        for tag in v:
            if len(tag) < 1 or len(tag) > 50:
                raise ValueError("Each tag must be 1-50 characters")
            if not tag.replace("-", "").replace("_", "").isalnum():
                raise ValueError("Tags can only contain alphanumeric characters, hyphens, and underscores")

        # Remove duplicates (case-insensitive)
        seen = set()
        unique_tags = []
        for tag in v:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag)

        return unique_tags


class URLUpdate(BaseSchema):
    """Schema for updating a URL."""

    tags: list[str] | None = Field(
        None,
        max_length=10,
        description="Updated tags for the URL",
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags."""
        if v is None:
            return v

        for tag in v:
            if len(tag) < 1 or len(tag) > 50:
                raise ValueError("Each tag must be 1-50 characters")

        return v


class URLResponse(BaseSchema):
    """Schema for URL response."""

    id: int = Field(..., description="Unique identifier")
    original_url: str = Field(..., description="The original long URL")
    short_code: str = Field(..., description="The generated short code")
    short_url: str = Field(..., description="The complete shortened URL")
    clicks: Annotated[int, Field(ge=0)] = Field(..., description="Number of times the URL has been accessed")
    created_at: datetime = Field(..., description="When the URL was created")
    tags: list[str] | None = Field(None, description="Tags associated with the URL")


class URLStats(BaseSchema, TimestampMixin):
    """Schema for detailed URL statistics."""

    id: int = Field(..., description="Unique identifier")
    original_url: str = Field(..., description="The original long URL")
    short_code: str = Field(..., description="The short code")
    clicks: Annotated[int, Field(ge=0)] = Field(..., description="Total number of clicks")
    tags: list[str] | None = Field(None, description="Tags associated with the URL")


class URLListParams(BaseSchema):
    """Parameters for listing URLs."""

    limit: Annotated[int, Field(ge=1, le=1000)] = Field(
        default=100,
        description="Maximum number of URLs to return"
    )
    offset: Annotated[int, Field(ge=0)] = Field(
        default=0,
        description="Number of URLs to skip"
    )
    sort_by: str = Field(
        default="created_at",
        description="Field to sort by (created_at, clicks, short_code)"
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order (asc or desc)"
    )
    tag: str | None = Field(
        None,
        description="Filter by tag"
    )

    @field_validator("sort_by")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        """Validate sort field."""
        allowed = {"created_at", "updated_at", "clicks", "short_code"}
        if v not in allowed:
            raise ValueError(f"Invalid sort_by field. Allowed: {allowed}")
        return v


class URLBulkCreate(BaseSchema):
    """Schema for bulk URL creation."""

    urls: list[URLCreate] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of URLs to create"
    )

    @model_validator(mode="after")
    def validate_bulk_limits(self) -> "URLBulkCreate":
        """Validate bulk operation limits."""
        # Check for duplicate custom codes within the batch
        custom_codes = [u.custom_code for u in self.urls if u.custom_code]
        if len(custom_codes) != len(set(custom_codes)):
            raise ValueError("Duplicate custom codes found in batch")

        return self


class URLBulkResponse(BaseSchema):
    """Response for bulk URL creation."""

    success_count: Annotated[int, Field(ge=0)] = Field(
        ...,
        description="Number of successfully created URLs"
    )
    error_count: Annotated[int, Field(ge=0)] = Field(
        ...,
        description="Number of failed URL creations"
    )
    created_urls: list[URLResponse] = Field(
        default_factory=list,
        description="Successfully created URLs"
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Error messages for failed creations"
    )
