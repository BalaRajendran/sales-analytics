"""
Advanced validation schemas and utilities for URL Shortener.

Provides comprehensive validation for URLs, custom codes, and query parameters.
"""

import re
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, TypeAdapter, field_validator, model_validator

# Create HTTP URL adapter for validation
http_url_adapter = TypeAdapter(HttpUrl)

# Custom type for validated URLs
Url = Annotated[str, BeforeValidator(lambda value: str(http_url_adapter.validate_python(value)))]


class URLValidationRules(BaseModel):
    """URL validation rules configuration."""

    max_url_length: Annotated[int, Field(ge=1, le=10000)] = Field(
        default=2048,
        description="Maximum URL length"
    )
    allowed_schemes: list[str] = Field(
        default=["http", "https"],
        description="Allowed URL schemes"
    )
    blocked_domains: list[str] = Field(
        default_factory=list,
        description="Blocked domains"
    )
    require_tld: bool = Field(
        default=True,
        description="Require valid TLD"
    )

    @field_validator("allowed_schemes")
    @classmethod
    def validate_schemes(cls, v: list[str]) -> list[str]:
        """Validate URL schemes."""
        valid_schemes = {"http", "https", "ftp", "ftps"}
        for scheme in v:
            if scheme.lower() not in valid_schemes:
                raise ValueError(f"Invalid scheme: {scheme}")
        return [s.lower() for s in v]


class ShortCodeValidationRules(BaseModel):
    """Short code validation rules."""

    min_length: Annotated[int, Field(ge=3, le=20)] = Field(
        default=4,
        description="Minimum short code length"
    )
    max_length: Annotated[int, Field(ge=3, le=20)] = Field(
        default=10,
        description="Maximum short code length"
    )
    allowed_pattern: str = Field(
        default=r"^[a-zA-Z0-9_-]+$",
        description="Regex pattern for valid short codes"
    )
    reserved_codes: list[str] = Field(
        default_factory=lambda: [
            "api", "docs", "admin", "health", "metrics", "static",
            "assets", "favicon", "robots", "sitemap"
        ],
        description="Reserved short codes that cannot be used"
    )

    @field_validator("allowed_pattern")
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        """Validate regex pattern is compilable."""
        try:
            re.compile(v)
            return v
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}") from e

    @model_validator(mode="after")
    def validate_length_range(self) -> "ShortCodeValidationRules":
        """Validate min_length is less than max_length."""
        if self.min_length >= self.max_length:
            raise ValueError("min_length must be less than max_length")
        return self

    def is_valid_code(self, code: str) -> tuple[bool, str | None]:
        """
        Check if a code is valid.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check length
        if len(code) < self.min_length:
            return False, f"Short code must be at least {self.min_length} characters"
        if len(code) > self.max_length:
            return False, f"Short code must be at most {self.max_length} characters"

        # Check pattern
        if not re.match(self.allowed_pattern, code):
            return False, "Short code contains invalid characters"

        # Check reserved codes
        if code.lower() in [r.lower() for r in self.reserved_codes]:
            return False, f"Short code '{code}' is reserved"

        return True, None


class PaginationValidation(BaseModel):
    """Validated pagination parameters."""

    limit: Annotated[int, Field(ge=1, le=1000)] = Field(
        default=100,
        description="Number of items per page"
    )
    offset: Annotated[int, Field(ge=0)] = Field(
        default=0,
        description="Number of items to skip"
    )

    @model_validator(mode="after")
    def validate_pagination(self) -> "PaginationValidation":
        """Validate pagination parameters."""
        # Warn if offset is very large (potential performance issue)
        if self.offset > 10000:
            raise ValueError("Offset too large. Use cursor-based pagination for better performance.")
        return self


class DateRangeValidation(BaseModel):
    """Validated date range parameters."""

    from_date: str | None = Field(None, description="Start date (ISO format)")
    to_date: str | None = Field(None, description="End date (ISO format)")

    @field_validator("from_date", "to_date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate date format."""
        if v is None:
            return v

        # Try to parse as ISO format
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS): {e}") from e

    @model_validator(mode="after")
    def validate_date_range(self) -> "DateRangeValidation":
        """Validate date range is logical."""
        if self.from_date and self.to_date:
            from datetime import datetime
            from_dt = datetime.fromisoformat(self.from_date.replace('Z', '+00:00'))
            to_dt = datetime.fromisoformat(self.to_date.replace('Z', '+00:00'))

            if from_dt >= to_dt:
                raise ValueError("from_date must be before to_date")

        return self


class SortValidation(BaseModel):
    """Validated sorting parameters."""

    sort_by: str = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", description="Sort order")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        """Validate sort field."""
        allowed_fields = {"created_at", "updated_at", "clicks", "short_code", "original_url"}
        if v not in allowed_fields:
            raise ValueError(f"Invalid sort field: {v}. Allowed: {allowed_fields}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        if v.lower() not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v.lower()


def validate_url_safety(url: str) -> tuple[bool, str | None]:
    """
    Validate URL for safety concerns.

    Checks for:
    - Suspicious patterns
    - Known malicious domains
    - URL encoding attacks

    Returns:
        Tuple of (is_safe, warning_message)
    """
    url_lower = url.lower()

    # Check for suspicious patterns
    suspicious_patterns = [
        "javascript:", "data:", "vbscript:", "file:",
        "<script", "onerror=", "onclick=",
        "../", "..\\",
        "%00", "\x00"
    ]

    for pattern in suspicious_patterns:
        if pattern in url_lower:
            return False, f"URL contains suspicious pattern: {pattern}"

    # Check for excessive URL encoding (potential obfuscation)
    if url.count('%') > 10:
        return False, "URL contains excessive URL encoding"

    # Check for very long URLs (potential DoS)
    if len(url) > 2048:
        return False, "URL is too long (max 2048 characters)"

    return True, None


def validate_custom_code(code: str, rules: ShortCodeValidationRules) -> tuple[bool, str | None]:
    """
    Validate custom short code against rules.

    Args:
        code: The custom code to validate
        rules: Validation rules to apply

    Returns:
        Tuple of (is_valid, error_message)
    """
    return rules.is_valid_code(code)


# Default validation rules
DEFAULT_URL_RULES = URLValidationRules()
DEFAULT_SHORT_CODE_RULES = ShortCodeValidationRules()
