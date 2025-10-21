"""
Sales representative service for sales rep operations.

Handles all sales rep CRUD operations with cache management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache_decorators import cached
from src.core.config import settings
from src.models.order import Order
from src.models.sales_rep import SalesRepresentative
from src.services.cache_invalidation import cache_invalidation_service


class SalesRepService:
    """Service for sales representative operations."""

    @staticmethod
    @cached(key_prefix="sales_rep:detail", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_sales_rep_by_id(
        db: AsyncSession, sales_rep_id: UUID
    ) -> Optional[SalesRepresentative]:
        """
        Get a sales representative by ID.

        Args:
            db: Database session
            sales_rep_id: Sales rep UUID

        Returns:
            Sales representative or None if not found
        """
        stmt = select(SalesRepresentative).where(SalesRepresentative.id == sales_rep_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_sales_rep_by_email(
        db: AsyncSession, email: str
    ) -> Optional[SalesRepresentative]:
        """
        Get a sales representative by email.

        Args:
            db: Database session
            email: Sales rep email

        Returns:
            Sales representative or None if not found
        """
        stmt = select(SalesRepresentative).where(SalesRepresentative.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_sales_reps(
        db: AsyncSession,
        region: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[SalesRepresentative], int]:
        """
        Get paginated list of sales representatives with filters.

        Args:
            db: Database session
            region: Filter by region
            limit: Page size
            offset: Page offset

        Returns:
            Tuple of (sales reps list, total count)
        """
        # Build query
        stmt = select(SalesRepresentative)

        # Apply filters
        if region:
            stmt = stmt.where(SalesRepresentative.region == region)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination and execute
        stmt = stmt.limit(limit).offset(offset).order_by(SalesRepresentative.name)
        result = await db.execute(stmt)
        sales_reps = result.scalars().all()

        return list(sales_reps), total_count

    @staticmethod
    async def create_sales_rep(
        db: AsyncSession,
        name: str,
        email: str,
        region: Optional[str] = None,
        commission_rate: Optional[Decimal] = None,
    ) -> SalesRepresentative:
        """
        Create a new sales representative.

        Args:
            db: Database session
            name: Sales rep name
            email: Sales rep email
            region: Region (optional)
            commission_rate: Commission rate percentage (optional)

        Returns:
            Created sales representative

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Validation
        if not name or not name.strip():
            raise ValueError("Sales representative name is required")
        if not email or not email.strip():
            raise ValueError("Sales representative email is required")

        if commission_rate is not None:
            if commission_rate < 0 or commission_rate > 100:
                raise ValueError("Commission rate must be between 0 and 100")

        # Check if email already exists
        existing = await SalesRepService.get_sales_rep_by_email(db, email)
        if existing:
            raise ValueError(f"Sales representative with email {email} already exists")

        # Create sales rep
        sales_rep = SalesRepresentative(
            id=uuid4(),
            name=name.strip(),
            email=email.strip().lower(),
            region=region,
            commission_rate=commission_rate,
        )

        db.add(sales_rep)
        await db.commit()
        await db.refresh(sales_rep)

        # Invalidate caches
        await cache_invalidation_service.invalidate_sales_rep_cache()
        await cache_invalidation_service.invalidate_dashboard_cache()

        return sales_rep

    @staticmethod
    async def update_sales_rep(
        db: AsyncSession,
        sales_rep_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        region: Optional[str] = None,
        commission_rate: Optional[Decimal] = None,
    ) -> Optional[SalesRepresentative]:
        """
        Update a sales representative.

        Args:
            db: Database session
            sales_rep_id: Sales rep UUID
            name: New name (optional)
            email: New email (optional)
            region: New region (optional)
            commission_rate: New commission rate (optional)

        Returns:
            Updated sales representative or None if not found

        Raises:
            ValueError: If validation fails or email already exists
        """
        # Get sales rep
        sales_rep = await SalesRepService.get_sales_rep_by_id(db, sales_rep_id)
        if not sales_rep:
            return None

        # Update fields
        if name is not None:
            if not name.strip():
                raise ValueError("Sales representative name cannot be empty")
            sales_rep.name = name.strip()

        if email is not None:
            email = email.strip().lower()
            # Check if new email is unique
            existing = await SalesRepService.get_sales_rep_by_email(db, email)
            if existing and existing.id != sales_rep_id:
                raise ValueError(f"Sales representative with email {email} already exists")
            sales_rep.email = email

        if region is not None:
            sales_rep.region = region

        if commission_rate is not None:
            if commission_rate < 0 or commission_rate > 100:
                raise ValueError("Commission rate must be between 0 and 100")
            sales_rep.commission_rate = commission_rate

        await db.commit()
        await db.refresh(sales_rep)

        # Invalidate caches
        await cache_invalidation_service.on_sales_rep_updated(sales_rep_id)

        return sales_rep

    @staticmethod
    async def delete_sales_rep(db: AsyncSession, sales_rep_id: UUID) -> bool:
        """
        Delete a sales representative.

        Args:
            db: Database session
            sales_rep_id: Sales rep UUID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If sales rep has associated orders
        """
        # Get sales rep
        sales_rep = await SalesRepService.get_sales_rep_by_id(db, sales_rep_id)
        if not sales_rep:
            return False

        # Check for associated orders
        check_stmt = select(Order).where(Order.sales_rep_id == sales_rep_id).limit(1)
        check_result = await db.execute(check_stmt)
        if check_result.scalar_one_or_none():
            raise ValueError("Cannot delete sales representative with existing orders")

        # Delete sales rep
        await db.delete(sales_rep)
        await db.commit()

        # Invalidate caches
        await cache_invalidation_service.invalidate_sales_rep_cache(sales_rep_id)
        await cache_invalidation_service.invalidate_dashboard_cache()

        return True

    @staticmethod
    async def get_sales_rep_performance(
        db: AsyncSession,
        sales_rep_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """
        Get performance metrics for a sales representative.

        Args:
            db: Database session
            sales_rep_id: Sales rep UUID
            start_date: Start date for metrics (optional)
            end_date: End date for metrics (optional)

        Returns:
            Dictionary with performance metrics
        """
        # Build query
        stmt = (
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(
                    func.case((Order.status == "completed", 1), else_=0)
                ).label("completed_orders"),
                func.sum(Order.total_amount).label("total_sales"),
                func.avg(Order.total_amount).label("avg_order_value"),
                func.max(Order.order_date).label("last_order_date"),
            )
            .where(Order.sales_rep_id == sales_rep_id)
        )

        # Apply date filters if provided
        if start_date:
            stmt = stmt.where(Order.order_date >= start_date)
        if end_date:
            stmt = stmt.where(Order.order_date <= end_date)

        result = await db.execute(stmt)
        row = result.one()

        # Get sales rep for commission calculation
        sales_rep = await SalesRepService.get_sales_rep_by_id(db, sales_rep_id)

        # Calculate commission
        commission_earned = Decimal("0.00")
        if sales_rep and sales_rep.commission_rate and row.total_sales:
            commission_earned = row.total_sales * sales_rep.commission_rate / 100

        return {
            "sales_rep_id": sales_rep_id,
            "total_orders": row.total_orders or 0,
            "completed_orders": row.completed_orders or 0,
            "total_sales": row.total_sales or Decimal("0.00"),
            "avg_order_value": row.avg_order_value or Decimal("0.00"),
            "commission_earned": commission_earned,
            "last_order_date": row.last_order_date,
        }

    @staticmethod
    @cached(key_prefix="sales_rep:leaderboard", ttl=settings.CACHE_TTL_DASHBOARD)
    async def get_sales_rep_leaderboard(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
    ) -> list[dict]:
        """
        Get sales representative leaderboard by revenue.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            limit: Number of reps to return

        Returns:
            List of sales reps with performance metrics
        """
        stmt = (
            select(
                SalesRepresentative.id,
                SalesRepresentative.name,
                SalesRepresentative.region,
                SalesRepresentative.commission_rate,
                func.count(Order.id).label("orders_count"),
                func.sum(Order.total_amount).label("total_sales"),
                func.avg(Order.total_amount).label("avg_order_value"),
            )
            .join(Order, SalesRepresentative.id == Order.sales_rep_id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(
                SalesRepresentative.id,
                SalesRepresentative.name,
                SalesRepresentative.region,
                SalesRepresentative.commission_rate,
            )
            .order_by(func.sum(Order.total_amount).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "rank": idx + 1,
                "sales_rep_id": row.id,
                "sales_rep_name": row.name,
                "region": row.region,
                "orders_count": row.orders_count,
                "total_sales": row.total_sales or Decimal("0.00"),
                "avg_order_value": row.avg_order_value or Decimal("0.00"),
                "commission_earned": (
                    row.total_sales * row.commission_rate / 100
                    if row.commission_rate
                    else Decimal("0.00")
                ),
            }
            for idx, row in enumerate(rows)
        ]

    @staticmethod
    @cached(key_prefix="sales_rep:by_region", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_sales_reps_by_region(db: AsyncSession) -> dict[str, list[SalesRepresentative]]:
        """
        Get sales representatives grouped by region.

        Args:
            db: Database session

        Returns:
            Dictionary mapping region to list of sales reps
        """
        stmt = select(SalesRepresentative).order_by(
            SalesRepresentative.region, SalesRepresentative.name
        )

        result = await db.execute(stmt)
        sales_reps = result.scalars().all()

        # Group by region
        by_region: dict[str, list[SalesRepresentative]] = {}
        for sales_rep in sales_reps:
            region = sales_rep.region or "Unknown"
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(sales_rep)

        return by_region

    @staticmethod
    async def get_region_performance(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict]:
        """
        Get performance metrics by region.

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            List of region performance metrics
        """
        stmt = (
            select(
                SalesRepresentative.region,
                func.count(func.distinct(SalesRepresentative.id)).label("reps_count"),
                func.count(Order.id).label("orders_count"),
                func.sum(Order.total_amount).label("total_revenue"),
                func.avg(Order.total_amount).label("avg_order_value"),
            )
            .join(Order, SalesRepresentative.id == Order.sales_rep_id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(SalesRepresentative.region)
            .order_by(func.sum(Order.total_amount).desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        total_revenue = sum(row.total_revenue for row in rows) or Decimal("0.00")

        return [
            {
                "region": row.region or "Unknown",
                "sales_reps_count": row.reps_count,
                "orders_count": row.orders_count,
                "total_revenue": row.total_revenue or Decimal("0.00"),
                "avg_order_value": row.avg_order_value or Decimal("0.00"),
                "revenue_contribution_percentage": (
                    float(row.total_revenue / total_revenue * 100) if total_revenue > 0 else 0.0
                ),
            }
            for row in rows
        ]

    @staticmethod
    async def assign_sales_rep_to_order(
        db: AsyncSession, order_id: UUID, sales_rep_id: UUID
    ) -> bool:
        """
        Assign a sales representative to an order.

        Args:
            db: Database session
            order_id: Order UUID
            sales_rep_id: Sales rep UUID

        Returns:
            True if successful

        Raises:
            ValueError: If order or sales rep not found
        """
        # Verify sales rep exists
        sales_rep = await SalesRepService.get_sales_rep_by_id(db, sales_rep_id)
        if not sales_rep:
            raise ValueError(f"Sales representative {sales_rep_id} not found")

        # Get order
        from src.services.order_service import order_service

        order = await order_service.get_order_by_id(db, order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        # Update order
        order.sales_rep_id = sales_rep_id
        await db.commit()

        # Invalidate caches
        await cache_invalidation_service.invalidate_sales_rep_cache(sales_rep_id)
        await cache_invalidation_service.on_order_updated(order_id, order.customer_id, False)

        return True


# Singleton instance
sales_rep_service = SalesRepService()
