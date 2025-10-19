# 📘 Sales Dashboard API Template Guide

This guide will help you quickly build your sales dashboard APIs using the established patterns in this template.

## 🎯 Quick Start: Building Your First Sales API

Follow these steps to create a complete API endpoint for your sales dashboard:

### Step 1: Define Your Data Model

Create a new file: `src/models/sale.py`

```python
"""Sale model for sales dashboard."""

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Sale(Base):
    """Sales transaction model."""

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Sale details
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Timestamps
    sale_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, product={self.product_name}, amount={self.amount})>"
```

### Step 2: Create Pydantic Schemas

Create a new file: `src/schemas/sale.py`

```python
"""Sale schemas for request/response validation."""

from datetime import datetime
from typing import Annotated
from pydantic import Field, field_validator

from src.schemas.common import BaseSchema, TimestampMixin


class SaleCreate(BaseSchema):
    """Schema for creating a new sale."""

    product_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product name"
    )
    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Customer name"
    )
    amount: Annotated[float, Field(gt=0)] = Field(
        ...,
        description="Sale amount (must be positive)"
    )
    quantity: Annotated[int, Field(ge=1)] = Field(
        default=1,
        description="Quantity sold"
    )
    sale_date: datetime = Field(
        ...,
        description="Date of sale"
    )


class SaleResponse(BaseSchema):
    """Schema for sale response."""

    id: int
    product_name: str
    customer_name: str
    amount: float
    quantity: int
    sale_date: datetime
    created_at: datetime
    updated_at: datetime


class SaleUpdate(BaseSchema):
    """Schema for updating a sale."""

    product_name: str | None = None
    customer_name: str | None = None
    amount: Annotated[float, Field(gt=0)] | None = None
    quantity: Annotated[int, Field(ge=1)] | None = None
    sale_date: datetime | None = None
```

### Step 3: Implement Business Logic Service

Create a new file: `src/services/sale_service.py`

```python
"""Sale service for business logic."""

from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sale import Sale
from src.schemas.sale import SaleCreate, SaleUpdate


class SaleService:
    """Service for sale operations."""

    @staticmethod
    async def create(db: AsyncSession, data: SaleCreate) -> Sale:
        """Create a new sale."""
        sale = Sale(
            product_name=data.product_name,
            customer_name=data.customer_name,
            amount=data.amount,
            quantity=data.quantity,
            sale_date=data.sale_date,
        )
        db.add(sale)
        await db.flush()
        await db.refresh(sale)
        return sale

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> Sale | None:
        """Get sale by ID."""
        result = await db.execute(select(Sale).where(Sale.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> list[Sale]:
        """Get all sales with optional date filtering."""
        query = select(Sale)

        # Apply date filters
        if start_date:
            query = query.where(Sale.sale_date >= start_date)
        if end_date:
            query = query.where(Sale.sale_date <= end_date)

        query = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, id: int, data: SaleUpdate) -> Sale | None:
        """Update a sale."""
        sale = await SaleService.get_by_id(db, id)
        if not sale:
            return None

        if data.product_name is not None:
            sale.product_name = data.product_name
        if data.customer_name is not None:
            sale.customer_name = data.customer_name
        if data.amount is not None:
            sale.amount = data.amount
        if data.quantity is not None:
            sale.quantity = data.quantity
        if data.sale_date is not None:
            sale.sale_date = data.sale_date

        await db.flush()
        await db.refresh(sale)
        return sale

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        """Delete a sale."""
        sale = await SaleService.get_by_id(db, id)
        if not sale:
            return False
        await db.delete(sale)
        await db.flush()
        return True

    @staticmethod
    async def get_total_revenue(
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> float:
        """Calculate total revenue for a date range."""
        query = select(func.sum(Sale.amount))

        if start_date:
            query = query.where(Sale.sale_date >= start_date)
        if end_date:
            query = query.where(Sale.sale_date <= end_date)

        result = await db.execute(query)
        total = result.scalar()
        return total or 0.0
```

### Step 4: Create API Endpoints

Create a new file: `src/api/v1/endpoints/sales.py`

```python
"""Sales API endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import NotFoundError, InternalServerError
from src.schemas.common import ApiResponse
from src.schemas.sale import SaleCreate, SaleUpdate, SaleResponse
from src.services.sale_service import SaleService

router = APIRouter()


@router.post("/", response_model=ApiResponse[SaleResponse], status_code=status.HTTP_201_CREATED)
async def create_sale(
    data: SaleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new sale."""
    try:
        sale = await SaleService.create(db, data)
        await db.commit()

        response = SaleResponse(
            id=sale.id,
            product_name=sale.product_name,
            customer_name=sale.customer_name,
            amount=sale.amount,
            quantity=sale.quantity,
            sale_date=sale.sale_date,
            created_at=sale.created_at,
            updated_at=sale.updated_at,
        )
        return ApiResponse.success_response(response)

    except ValueError as e:
        raise InternalServerError(message=str(e)) from e


@router.get("/", response_model=ApiResponse[list[SaleResponse]])
async def list_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all sales with optional date filtering."""
    sales = await SaleService.get_all(db, skip, limit, start_date, end_date)

    response_list = [
        SaleResponse(
            id=sale.id,
            product_name=sale.product_name,
            customer_name=sale.customer_name,
            amount=sale.amount,
            quantity=sale.quantity,
            sale_date=sale.sale_date,
            created_at=sale.created_at,
            updated_at=sale.updated_at,
        )
        for sale in sales
    ]
    return ApiResponse.success_response(response_list)


@router.get("/{id}", response_model=ApiResponse[SaleResponse])
async def get_sale(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single sale by ID."""
    sale = await SaleService.get_by_id(db, id)
    if not sale:
        raise NotFoundError(message=f"Sale with ID {id} not found")

    response = SaleResponse(
        id=sale.id,
        product_name=sale.product_name,
        customer_name=sale.customer_name,
        amount=sale.amount,
        quantity=sale.quantity,
        sale_date=sale.sale_date,
        created_at=sale.created_at,
        updated_at=sale.updated_at,
    )
    return ApiResponse.success_response(response)


@router.put("/{id}", response_model=ApiResponse[SaleResponse])
async def update_sale(
    id: int,
    data: SaleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a sale."""
    sale = await SaleService.update(db, id, data)
    if not sale:
        raise NotFoundError(message=f"Sale with ID {id} not found")

    await db.commit()

    response = SaleResponse(
        id=sale.id,
        product_name=sale.product_name,
        customer_name=sale.customer_name,
        amount=sale.amount,
        quantity=sale.quantity,
        sale_date=sale.sale_date,
        created_at=sale.created_at,
        updated_at=sale.updated_at,
    )
    return ApiResponse.success_response(response)


@router.delete("/{id}", response_model=ApiResponse[dict])
async def delete_sale(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a sale."""
    deleted = await SaleService.delete(db, id)
    if not deleted:
        raise NotFoundError(message=f"Sale with ID {id} not found")

    await db.commit()
    return ApiResponse.success_response({"message": f"Sale {id} deleted successfully"})


@router.get("/stats/revenue", response_model=ApiResponse[dict])
async def get_revenue_stats(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get revenue statistics for a date range."""
    total_revenue = await SaleService.get_total_revenue(db, start_date, end_date)

    return ApiResponse.success_response({
        "total_revenue": total_revenue,
        "start_date": start_date,
        "end_date": end_date
    })
```

### Step 5: Register Your API Router

Edit `src/api/v1/__init__.py`:

```python
"""API v1 router."""

from fastapi import APIRouter
from src.api.v1.endpoints import sales  # Import your sales endpoints

api_router = APIRouter()

# Register sales endpoints
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
```

### Step 6: Update Model Imports

Edit `src/models/__init__.py`:

```python
"""Database models."""

from src.models.sale import Sale

__all__ = ["Sale"]
```

Edit `src/schemas/__init__.py`:

```python
"""Pydantic schemas."""

from src.schemas.sale import SaleCreate, SaleResponse, SaleUpdate

__all__ = ["SaleCreate", "SaleResponse", "SaleUpdate"]
```

### Step 7: Create and Run Database Migration

```bash
# Create migration for your new Sale model
make migration

# Apply the migration
make migrate
```

### Step 8: Test Your API

```bash
# Start the server
make run

# Visit http://localhost:8000/api/v1/docs
# Your new sales endpoints will be available at:
# - POST   /api/v1/sales/
# - GET    /api/v1/sales/
# - GET    /api/v1/sales/{id}
# - PUT    /api/v1/sales/{id}
# - DELETE /api/v1/sales/{id}
# - GET    /api/v1/sales/stats/revenue
```

## 🔄 Pattern Summary

Every feature follows this pattern:

```
Model (Database) → Schema (Validation) → Service (Logic) → Endpoint (API) → Router (Registration)
```

1. **Model**: Define database structure
2. **Schema**: Define request/response validation
3. **Service**: Implement business logic
4. **Endpoint**: Create API routes
5. **Router**: Register endpoints

## 📦 Common Patterns Included

### Pagination
```python
skip: int = 0
limit: int = 100
```

### Filtering
```python
search: str | None = None
start_date: datetime | None = None
end_date: datetime | None = None
```

### Sorting
```python
sort_by: str = "created_at"
sort_order: str = "desc"  # asc or desc
```

### Error Handling
```python
from src.core.exceptions import NotFoundError, InternalServerError

if not resource:
    raise NotFoundError(message="Resource not found")
```

### Response Format
All responses use the standardized `ApiResponse` wrapper:
```python
return ApiResponse.success_response(data)
```

## 🎨 Additional Features to Build

Consider adding these common sales dashboard features:

1. **Products API** - Manage product catalog
2. **Customers API** - Customer management
3. **Orders API** - Order tracking
4. **Analytics API** - Revenue, trends, insights
5. **Reports API** - Generate sales reports
6. **Dashboard API** - Summary statistics

For each feature, follow the same pattern shown above!

## 📚 Next Steps

1. Review the template files in:
   - `src/models/example_model.py`
   - `src/schemas/example_schema.py`
   - `src/services/example_service.py`
   - `src/api/v1/endpoints/example_endpoints.py`

2. Check the documentation in `docs/` folder

3. Run the example tests to understand testing patterns

4. Deploy using the Docker setup in `docker-compose.yml`

Happy coding! 🚀
