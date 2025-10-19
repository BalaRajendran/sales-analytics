"""
Example Schema Template.

This is a template file showing the pattern for creating Pydantic schemas.
Replace this with your actual sales dashboard schemas.
"""

from datetime import datetime
from typing import Annotated

from pydantic import Field, field_validator

from src.schemas.common import BaseSchema, TimestampMixin


# Create Schema - Used for POST requests
class ExampleCreate(BaseSchema):
    """
    Schema for creating a new record.

    Example for Sales Dashboard:
    - SaleCreate
    - ProductCreate
    - CustomerCreate
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the item",
        examples=["Example Item"]
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Optional description"
    )
    amount: Annotated[float, Field(ge=0)] = Field(
        ...,
        description="Amount (must be non-negative)",
        examples=[99.99]
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()


# Update Schema - Used for PUT/PATCH requests
class ExampleUpdate(BaseSchema):
    """Schema for updating an existing record."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated name"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Updated description"
    )
    amount: Annotated[float, Field(ge=0)] | None = Field(
        None,
        description="Updated amount"
    )


# Response Schema - Used for API responses
class ExampleResponse(BaseSchema):
    """Schema for API response."""

    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the item")
    description: str | None = Field(None, description="Description")
    amount: float = Field(..., description="Amount")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# Detail Schema - For detailed views with statistics
class ExampleDetail(BaseSchema, TimestampMixin):
    """Schema for detailed view with additional statistics."""

    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")
    description: str | None = Field(None, description="Description")
    amount: float = Field(..., description="Amount")
    # Add any computed fields or statistics here


# List Parameters Schema - For filtering/sorting list endpoints
class ExampleListParams(BaseSchema):
    """Parameters for listing records."""

    limit: Annotated[int, Field(ge=1, le=1000)] = Field(
        default=100,
        description="Maximum number of items to return"
    )
    offset: Annotated[int, Field(ge=0)] = Field(
        default=0,
        description="Number of items to skip"
    )
    sort_by: str = Field(
        default="created_at",
        description="Field to sort by"
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order (asc or desc)"
    )
    search: str | None = Field(
        None,
        max_length=255,
        description="Search query"
    )

    @field_validator("sort_by")
    @classmethod
    def validate_sort_field(cls, v: str) -> str:
        """Validate sort field."""
        allowed = {"created_at", "updated_at", "name", "amount"}
        if v not in allowed:
            raise ValueError(f"Invalid sort_by field. Allowed: {', '.join(allowed)}")
        return v
