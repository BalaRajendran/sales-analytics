"""
Example Endpoints Template.

This is a template file showing the pattern for creating API endpoints.
Replace this with your actual sales dashboard endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import NotFoundError, InternalServerError
from src.schemas.common import ApiResponse, PaginatedResponse
from src.schemas.example_schema import (
    ExampleCreate,
    ExampleUpdate,
    ExampleResponse,
    ExampleDetail,
    ExampleListParams
)
from src.services.example_service import ExampleService

router = APIRouter()


@router.post(
    "/",
    response_model=ApiResponse[ExampleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new record",
    tags=["Examples"]
)
async def create_example(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new record.

    Example for Sales Dashboard:
    - Create a new sale
    - Create a new product
    - Create a new customer
    """
    try:
        instance = await ExampleService.create(db, data)
        await db.commit()

        response = ExampleResponse(
            id=instance.id,
            name=instance.name,
            description=instance.description,
            amount=instance.amount,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )
        return ApiResponse.success_response(response)

    except ValueError as e:
        raise InternalServerError(message=str(e)) from e


@router.get(
    "/",
    response_model=ApiResponse[list[ExampleResponse]],
    summary="List all records",
    tags=["Examples"]
)
async def list_examples(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    """
    List all records with pagination, filtering, and sorting.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **search**: Search query to filter results (optional)
    - **sort_by**: Field to sort by (default: created_at)
    - **sort_order**: Sort order - asc or desc (default: desc)
    """
    instances = await ExampleService.get_all(
        db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    response_list = [
        ExampleResponse(
            id=instance.id,
            name=instance.name,
            description=instance.description,
            amount=instance.amount,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )
        for instance in instances
    ]

    return ApiResponse.success_response(response_list)


@router.get(
    "/{id}",
    response_model=ApiResponse[ExampleDetail],
    summary="Get a record by ID",
    tags=["Examples"]
)
async def get_example(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single record by its ID.

    - **id**: The unique identifier of the record
    """
    instance = await ExampleService.get_by_id(db, id)

    if not instance:
        raise NotFoundError(message=f"Record with ID {id} not found")

    response = ExampleDetail(
        id=instance.id,
        name=instance.name,
        description=instance.description,
        amount=instance.amount,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    )

    return ApiResponse.success_response(response)


@router.put(
    "/{id}",
    response_model=ApiResponse[ExampleResponse],
    summary="Update a record",
    tags=["Examples"]
)
async def update_example(
    id: int,
    data: ExampleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing record.

    - **id**: The unique identifier of the record to update
    - **data**: The fields to update (all fields are optional)
    """
    instance = await ExampleService.update(db, id, data)

    if not instance:
        raise NotFoundError(message=f"Record with ID {id} not found")

    await db.commit()

    response = ExampleResponse(
        id=instance.id,
        name=instance.name,
        description=instance.description,
        amount=instance.amount,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    )

    return ApiResponse.success_response(response)


@router.delete(
    "/{id}",
    response_model=ApiResponse[dict],
    summary="Delete a record",
    tags=["Examples"]
)
async def delete_example(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a record by its ID.

    - **id**: The unique identifier of the record to delete
    """
    deleted = await ExampleService.delete(db, id)

    if not deleted:
        raise NotFoundError(message=f"Record with ID {id} not found")

    await db.commit()

    return ApiResponse.success_response({
        "message": f"Record with ID {id} deleted successfully"
    })


# Additional endpoint example: Statistics or aggregated data
@router.get(
    "/stats/summary",
    response_model=ApiResponse[dict],
    summary="Get summary statistics",
    tags=["Examples", "Statistics"]
)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary statistics for all records.

    Example for Sales Dashboard:
    - Total revenue
    - Number of sales
    - Average order value
    - Top performing products
    """
    total_count = await ExampleService.count(db)

    # Add more statistics as needed
    stats = {
        "total_count": total_count,
        # Add more computed statistics here
    }

    return ApiResponse.success_response(stats)
