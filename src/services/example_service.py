"""
Example Service Template.

This is a template file showing the pattern for creating service classes.
Services contain the business logic for your application.
Replace this with your actual sales dashboard services.
"""

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.example_model import ExampleModel
from src.schemas.example_schema import ExampleCreate, ExampleUpdate


class ExampleService:
    """
    Service class for business logic.

    Example for Sales Dashboard:
    - SaleService
    - ProductService
    - CustomerService
    - RevenueService
    """

    @staticmethod
    async def create(
        db: AsyncSession,
        data: ExampleCreate
    ) -> ExampleModel:
        """
        Create a new record.

        Args:
            db: Database session
            data: Creation data

        Returns:
            Created model instance

        Raises:
            ValueError: If validation fails
        """
        # Create new instance
        instance = ExampleModel(
            name=data.name,
            description=data.description,
            amount=data.amount,
        )

        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        id: int
    ) -> ExampleModel | None:
        """
        Get a record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        result = await db.execute(
            select(ExampleModel).where(ExampleModel.id == id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> list[ExampleModel]:
        """
        Get all records with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search query
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)

        Returns:
            List of model instances
        """
        query = select(ExampleModel)

        # Apply search filter if provided
        if search:
            query = query.where(
                or_(
                    ExampleModel.name.ilike(f"%{search}%"),
                    ExampleModel.description.ilike(f"%{search}%")
                )
            )

        # Apply sorting
        sort_column = getattr(ExampleModel, sort_by, ExampleModel.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        id: int,
        data: ExampleUpdate
    ) -> ExampleModel | None:
        """
        Update a record.

        Args:
            db: Database session
            id: Record ID
            data: Update data

        Returns:
            Updated model instance or None if not found
        """
        instance = await ExampleService.get_by_id(db, id)
        if not instance:
            return None

        # Update fields if provided
        if data.name is not None:
            instance.name = data.name
        if data.description is not None:
            instance.description = data.description
        if data.amount is not None:
            instance.amount = data.amount

        await db.flush()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def delete(
        db: AsyncSession,
        id: int
    ) -> bool:
        """
        Delete a record.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        instance = await ExampleService.get_by_id(db, id)
        if not instance:
            return False

        await db.delete(instance)
        await db.flush()
        return True

    @staticmethod
    async def count(
        db: AsyncSession,
        search: str | None = None
    ) -> int:
        """
        Count total records.

        Args:
            db: Database session
            search: Optional search query

        Returns:
            Total count
        """
        query = select(ExampleModel)

        if search:
            query = query.where(
                or_(
                    ExampleModel.name.ilike(f"%{search}%"),
                    ExampleModel.description.ilike(f"%{search}%")
                )
            )

        result = await db.execute(query)
        return len(list(result.scalars().all()))
