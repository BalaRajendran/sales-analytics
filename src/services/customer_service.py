"""
Customer service for customer operations.

Handles all customer CRUD operations with cache management.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache_decorators import cached
from src.core.config import settings
from src.models.customer import Customer
from src.models.order import Order
from src.services.cache_invalidation import cache_invalidation_service


class CustomerService:
    """Service for customer operations."""

    @staticmethod
    @cached(key_prefix="customer:detail", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_customer_by_id(db: AsyncSession, customer_id: UUID) -> Optional[Customer]:
        """
        Get a customer by ID.

        Args:
            db: Database session
            customer_id: Customer UUID

        Returns:
            Customer or None if not found
        """
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_by_email(db: AsyncSession, email: str) -> Optional[Customer]:
        """
        Get a customer by email.

        Args:
            db: Database session
            email: Customer email

        Returns:
            Customer or None if not found
        """
        stmt = select(Customer).where(Customer.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        segment: Optional[str] = None,
        min_lifetime_value: Optional[Decimal] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Customer], int]:
        """
        Get paginated list of customers with filters.

        Args:
            db: Database session
            segment: Filter by segment
            min_lifetime_value: Minimum lifetime value filter
            search: Search in name or email
            limit: Page size
            offset: Page offset

        Returns:
            Tuple of (customers list, total count)
        """
        # Build query
        stmt = select(Customer)

        # Apply filters
        if segment:
            stmt = stmt.where(Customer.segment == segment)
        if min_lifetime_value is not None:
            stmt = stmt.where(Customer.total_lifetime_value >= min_lifetime_value)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (Customer.name.ilike(search_pattern)) | (Customer.email.ilike(search_pattern))
            )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination and execute
        stmt = stmt.limit(limit).offset(offset).order_by(Customer.name)
        result = await db.execute(stmt)
        customers = result.scalars().all()

        return list(customers), total_count

    @staticmethod
    async def create_customer(
        db: AsyncSession,
        name: str,
        email: str,
        segment: Optional[str] = None,
    ) -> Customer:
        """
        Create a new customer.

        Args:
            db: Database session
            name: Customer name
            email: Customer email
            segment: Customer segment (optional)

        Returns:
            Created customer

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Validation
        if not name or not name.strip():
            raise ValueError("Customer name is required")
        if not email or not email.strip():
            raise ValueError("Customer email is required")

        # Check if email already exists
        existing = await CustomerService.get_customer_by_email(db, email)
        if existing:
            raise ValueError(f"Customer with email {email} already exists")

        # Create customer
        customer = Customer(
            id=uuid4(),
            name=name.strip(),
            email=email.strip().lower(),
            segment=segment,
        )

        db.add(customer)
        await db.commit()
        await db.refresh(customer)

        # Invalidate caches
        await cache_invalidation_service.invalidate_customer_cache()
        await cache_invalidation_service.invalidate_dashboard_cache()

        return customer

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        customer_id: UUID,
        name: Optional[str] = None,
        email: Optional[str] = None,
        segment: Optional[str] = None,
        total_lifetime_value: Optional[Decimal] = None,
    ) -> Optional[Customer]:
        """
        Update a customer.

        Args:
            db: Database session
            customer_id: Customer UUID
            name: New name (optional)
            email: New email (optional)
            segment: New segment (optional)
            total_lifetime_value: New lifetime value (optional)

        Returns:
            Updated customer or None if not found

        Raises:
            ValueError: If validation fails or email already exists
        """
        # Get customer
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return None

        # Update fields
        if name is not None:
            if not name.strip():
                raise ValueError("Customer name cannot be empty")
            customer.name = name.strip()

        if email is not None:
            email = email.strip().lower()
            # Check if new email is unique
            existing = await CustomerService.get_customer_by_email(db, email)
            if existing and existing.id != customer_id:
                raise ValueError(f"Customer with email {email} already exists")
            customer.email = email

        if segment is not None:
            customer.segment = segment

        if total_lifetime_value is not None:
            if total_lifetime_value < 0:
                raise ValueError("Lifetime value cannot be negative")
            customer.total_lifetime_value = total_lifetime_value

        await db.commit()
        await db.refresh(customer)

        # Invalidate caches
        await cache_invalidation_service.on_customer_updated(customer_id)

        return customer

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: UUID) -> bool:
        """
        Delete a customer.

        Args:
            db: Database session
            customer_id: Customer UUID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If customer has associated orders
        """
        # Get customer
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return False

        # Check for associated orders
        check_stmt = select(Order).where(Order.customer_id == customer_id).limit(1)
        check_result = await db.execute(check_stmt)
        if check_result.scalar_one_or_none():
            raise ValueError("Cannot delete customer with existing orders")

        # Delete customer
        await db.delete(customer)
        await db.commit()

        # Invalidate caches
        await cache_invalidation_service.invalidate_customer_cache(customer_id)
        await cache_invalidation_service.invalidate_dashboard_cache()

        return True

    @staticmethod
    async def calculate_lifetime_value(db: AsyncSession, customer_id: UUID) -> Decimal:
        """
        Calculate customer lifetime value from completed orders.

        Args:
            db: Database session
            customer_id: Customer UUID

        Returns:
            Total lifetime value
        """
        stmt = (
            select(func.sum(Order.total_amount))
            .where(Order.customer_id == customer_id)
            .where(Order.status == "completed")
        )

        result = await db.execute(stmt)
        ltv = result.scalar() or Decimal("0.00")

        return ltv

    @staticmethod
    async def update_lifetime_value(db: AsyncSession, customer_id: UUID) -> Optional[Customer]:
        """
        Recalculate and update customer lifetime value.

        Args:
            db: Database session
            customer_id: Customer UUID

        Returns:
            Updated customer or None if not found
        """
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return None

        # Calculate lifetime value
        ltv = await CustomerService.calculate_lifetime_value(db, customer_id)

        # Update customer
        customer.total_lifetime_value = ltv
        await db.commit()
        await db.refresh(customer)

        # Invalidate caches
        await cache_invalidation_service.invalidate_customer_cache(customer_id)

        return customer

    @staticmethod
    async def get_customer_order_stats(db: AsyncSession, customer_id: UUID) -> dict:
        """
        Get customer order statistics.

        Args:
            db: Database session
            customer_id: Customer UUID

        Returns:
            Dictionary with order statistics
        """
        stmt = (
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(
                    func.case((Order.status == "completed", 1), else_=0)
                ).label("completed_orders"),
                func.sum(
                    func.case((Order.status == "pending", 1), else_=0)
                ).label("pending_orders"),
                func.sum(Order.total_amount).label("total_spent"),
                func.avg(Order.total_amount).label("avg_order_value"),
                func.max(Order.order_date).label("last_order_date"),
            )
            .where(Order.customer_id == customer_id)
        )

        result = await db.execute(stmt)
        row = result.one()

        return {
            "total_orders": row.total_orders or 0,
            "completed_orders": row.completed_orders or 0,
            "pending_orders": row.pending_orders or 0,
            "total_spent": row.total_spent or Decimal("0.00"),
            "avg_order_value": row.avg_order_value or Decimal("0.00"),
            "last_order_date": row.last_order_date,
        }

    @staticmethod
    async def assign_segment(db: AsyncSession, customer_id: UUID) -> Optional[Customer]:
        """
        Automatically assign customer segment based on lifetime value.

        Segments:
        - Premium: LTV >= $10,000
        - Regular: LTV >= $1,000
        - New: LTV < $1,000 or no orders
        - At-Risk: No orders in last 90 days
        - Churned: No orders in last 180 days

        Args:
            db: Database session
            customer_id: Customer UUID

        Returns:
            Updated customer or None if not found
        """
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return None

        # Get order stats
        stats = await CustomerService.get_customer_order_stats(db, customer_id)
        ltv = stats["total_spent"]
        last_order = stats["last_order_date"]

        # Determine segment
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        ninety_days_ago = now - timedelta(days=90)
        oneeighty_days_ago = now - timedelta(days=180)

        if last_order and last_order < oneeighty_days_ago:
            segment = "Churned"
        elif last_order and last_order < ninety_days_ago:
            segment = "At-Risk"
        elif ltv >= Decimal("10000.00"):
            segment = "Premium"
        elif ltv >= Decimal("1000.00"):
            segment = "Regular"
        else:
            segment = "New"

        # Update customer
        customer.segment = segment
        await db.commit()
        await db.refresh(customer)

        # Invalidate caches
        await cache_invalidation_service.invalidate_customer_cache(customer_id)

        return customer

    @staticmethod
    @cached(key_prefix="customer:at_risk", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_at_risk_customers(db: AsyncSession, days: int = 90) -> list[Customer]:
        """
        Get customers who haven't ordered in specified days.

        Args:
            db: Database session
            days: Number of days threshold

        Returns:
            List of at-risk customers
        """
        from datetime import datetime, timedelta

        threshold_date = datetime.utcnow() - timedelta(days=days)

        # Get customers with their last order date
        stmt = (
            select(Customer, func.max(Order.order_date).label("last_order"))
            .join(Order, Customer.id == Order.customer_id)
            .group_by(Customer.id)
            .having(func.max(Order.order_date) < threshold_date)
            .order_by(func.max(Order.order_date))
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [row[0] for row in rows]

    @staticmethod
    @cached(key_prefix="customer:high_value", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_high_value_customers(
        db: AsyncSession, min_ltv: Decimal = Decimal("5000.00"), limit: int = 100
    ) -> list[Customer]:
        """
        Get high-value customers.

        Args:
            db: Database session
            min_ltv: Minimum lifetime value threshold
            limit: Maximum number of customers to return

        Returns:
            List of high-value customers
        """
        stmt = (
            select(Customer)
            .where(Customer.total_lifetime_value >= min_ltv)
            .order_by(Customer.total_lifetime_value.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def bulk_assign_segments(db: AsyncSession) -> int:
        """
        Bulk assign segments to all customers.

        Args:
            db: Database session

        Returns:
            Number of customers updated
        """
        # Get all customers
        stmt = select(Customer)
        result = await db.execute(stmt)
        customers = result.scalars().all()

        count = 0
        for customer in customers:
            await CustomerService.assign_segment(db, customer.id)
            count += 1

        # Invalidate all customer caches
        await cache_invalidation_service.invalidate_customer_cache()

        return count


# Singleton instance
customer_service = CustomerService()
