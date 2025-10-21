"""
Order service for order operations.

Handles all order CRUD operations with cache management and stock updates.
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
from src.models.order_item import OrderItem
from src.models.product import Product
from src.services.cache_invalidation import cache_invalidation_service
from src.services.customer_service import customer_service
from src.services.product_service import product_service


class OrderService:
    """Service for order operations."""

    @staticmethod
    @cached(key_prefix="order:detail", ttl=settings.CACHE_TTL_DASHBOARD)
    async def get_order_by_id(db: AsyncSession, order_id: UUID) -> Optional[Order]:
        """
        Get an order by ID.

        Args:
            db: Database session
            order_id: Order UUID

        Returns:
            Order or None if not found
        """
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_orders(
        db: AsyncSession,
        customer_id: Optional[UUID] = None,
        sales_rep_id: Optional[UUID] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Order], int]:
        """
        Get paginated list of orders with filters.

        Args:
            db: Database session
            customer_id: Filter by customer
            sales_rep_id: Filter by sales representative
            status: Filter by order status
            date_from: Filter by start date
            date_to: Filter by end date
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            limit: Page size
            offset: Page offset

        Returns:
            Tuple of (orders list, total count)
        """
        # Build query
        stmt = select(Order)

        # Apply filters
        if customer_id:
            stmt = stmt.where(Order.customer_id == customer_id)
        if sales_rep_id:
            stmt = stmt.where(Order.sales_rep_id == sales_rep_id)
        if status:
            stmt = stmt.where(Order.status == status)
        if date_from:
            stmt = stmt.where(Order.order_date >= date_from)
        if date_to:
            stmt = stmt.where(Order.order_date <= date_to)
        if min_amount is not None:
            stmt = stmt.where(Order.total_amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Order.total_amount <= max_amount)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination and execute
        stmt = stmt.limit(limit).offset(offset).order_by(Order.order_date.desc())
        result = await db.execute(stmt)
        orders = result.scalars().all()

        return list(orders), total_count

    @staticmethod
    async def create_order(
        db: AsyncSession,
        customer_id: UUID,
        items: list[dict],
        sales_rep_id: Optional[UUID] = None,
        order_date: Optional[datetime] = None,
    ) -> Order:
        """
        Create a new order with items.

        Args:
            db: Database session
            customer_id: Customer UUID
            items: List of order items (dicts with 'product_id', 'quantity', 'unit_price')
            sales_rep_id: Sales representative UUID (optional)
            order_date: Order date (defaults to now)

        Returns:
            Created order

        Raises:
            ValueError: If validation fails or insufficient stock
        """
        # Validation
        if not items:
            raise ValueError("Order must have at least one item")

        if order_date is None:
            order_date = datetime.utcnow()

        # Verify customer exists
        from src.services.customer_service import customer_service

        customer = await customer_service.get_customer_by_id(db, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Verify sales rep exists if provided
        if sales_rep_id:
            from src.services.sales_rep_service import sales_rep_service

            sales_rep = await sales_rep_service.get_sales_rep_by_id(db, sales_rep_id)
            if not sales_rep:
                raise ValueError(f"Sales representative {sales_rep_id} not found")

        # Verify products and check stock
        total_amount = Decimal("0.00")
        validated_items = []

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]
            unit_price = item_data.get("unit_price")

            if quantity <= 0:
                raise ValueError(f"Quantity must be positive for product {product_id}")

            # Get product
            product = await product_service.get_product_by_id(db, product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            # Check stock
            if product.stock_quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for product {product.name}. "
                    f"Available: {product.stock_quantity}, Requested: {quantity}"
                )

            # Use current selling price if not provided
            if unit_price is None:
                unit_price = product.selling_price

            item_total = unit_price * quantity
            total_amount += item_total

            validated_items.append(
                {
                    "product_id": product_id,
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": item_total,
                }
            )

        # Create order
        order = Order(
            id=uuid4(),
            customer_id=customer_id,
            sales_rep_id=sales_rep_id,
            order_date=order_date,
            total_amount=total_amount,
            status="pending",
        )

        db.add(order)
        await db.flush()  # Get order ID

        # Create order items and update stock
        for item_data in validated_items:
            order_item = OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
            )
            db.add(order_item)

            # Reduce stock
            await product_service.adjust_stock(
                db, item_data["product_id"], -item_data["quantity"]
            )

        await db.commit()
        await db.refresh(order)

        # Update customer lifetime value
        await customer_service.update_lifetime_value(db, customer_id)

        # Invalidate caches
        await cache_invalidation_service.on_order_created(order.id, customer_id)

        return order

    @staticmethod
    async def update_order_status(
        db: AsyncSession, order_id: UUID, new_status: str
    ) -> Optional[Order]:
        """
        Update order status.

        Args:
            db: Database session
            order_id: Order UUID
            new_status: New status

        Returns:
            Updated order or None if not found

        Raises:
            ValueError: If invalid status transition
        """
        valid_statuses = ["pending", "processing", "completed", "cancelled", "refunded"]
        if new_status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"
            )

        # Get order
        order = await OrderService.get_order_by_id(db, order_id)
        if not order:
            return None

        old_status = order.status

        # Validate status transitions
        if old_status == "completed" and new_status not in ["refunded"]:
            raise ValueError("Completed orders can only be refunded")
        if old_status == "cancelled":
            raise ValueError("Cannot change status of cancelled order")
        if old_status == "refunded":
            raise ValueError("Cannot change status of refunded order")

        # Handle stock adjustments for cancellation/refund
        if new_status in ["cancelled", "refunded"] and old_status not in [
            "cancelled",
            "refunded",
        ]:
            # Restore stock
            items_stmt = select(OrderItem).where(OrderItem.order_id == order_id)
            items_result = await db.execute(items_stmt)
            items = items_result.scalars().all()

            for item in items:
                await product_service.adjust_stock(db, item.product_id, item.quantity)

        # Update status
        order.status = new_status
        await db.commit()
        await db.refresh(order)

        # Update customer lifetime value if status affects it
        if new_status in ["completed", "cancelled", "refunded"]:
            await customer_service.update_lifetime_value(db, order.customer_id)

        # Invalidate caches
        status_changed = old_status != new_status
        await cache_invalidation_service.on_order_updated(
            order.id, order.customer_id, status_changed
        )

        return order

    @staticmethod
    async def cancel_order(db: AsyncSession, order_id: UUID) -> Optional[Order]:
        """
        Cancel an order.

        Args:
            db: Database session
            order_id: Order UUID

        Returns:
            Cancelled order or None if not found

        Raises:
            ValueError: If order cannot be cancelled
        """
        order = await OrderService.get_order_by_id(db, order_id)
        if not order:
            return None

        if order.status == "completed":
            raise ValueError("Cannot cancel completed order. Use refund instead.")
        if order.status == "cancelled":
            raise ValueError("Order is already cancelled")
        if order.status == "refunded":
            raise ValueError("Cannot cancel refunded order")

        return await OrderService.update_order_status(db, order_id, "cancelled")

    @staticmethod
    async def complete_order(db: AsyncSession, order_id: UUID) -> Optional[Order]:
        """
        Mark an order as completed.

        Args:
            db: Database session
            order_id: Order UUID

        Returns:
            Completed order or None if not found

        Raises:
            ValueError: If order cannot be completed
        """
        order = await OrderService.get_order_by_id(db, order_id)
        if not order:
            return None

        if order.status == "cancelled":
            raise ValueError("Cannot complete cancelled order")
        if order.status == "refunded":
            raise ValueError("Cannot complete refunded order")
        if order.status == "completed":
            return order  # Already completed

        return await OrderService.update_order_status(db, order_id, "completed")

    @staticmethod
    async def refund_order(db: AsyncSession, order_id: UUID) -> Optional[Order]:
        """
        Refund an order.

        Args:
            db: Database session
            order_id: Order UUID

        Returns:
            Refunded order or None if not found

        Raises:
            ValueError: If order cannot be refunded
        """
        order = await OrderService.get_order_by_id(db, order_id)
        if not order:
            return None

        if order.status != "completed":
            raise ValueError("Only completed orders can be refunded")
        if order.status == "refunded":
            return order  # Already refunded

        return await OrderService.update_order_status(db, order_id, "refunded")

    @staticmethod
    async def get_order_items(db: AsyncSession, order_id: UUID) -> list[OrderItem]:
        """
        Get all items for an order.

        Args:
            db: Database session
            order_id: Order UUID

        Returns:
            List of order items
        """
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_order_total_profit(db: AsyncSession, order_id: UUID) -> Decimal:
        """
        Calculate total profit for an order.

        Args:
            db: Database session
            order_id: Order UUID

        Returns:
            Total profit
        """
        stmt = (
            select(
                func.sum(
                    OrderItem.quantity * (OrderItem.unit_price - Product.cost_price)
                ).label("profit")
            )
            .join(Product, OrderItem.product_id == Product.id)
            .where(OrderItem.order_id == order_id)
        )

        result = await db.execute(stmt)
        profit = result.scalar() or Decimal("0.00")

        return profit

    @staticmethod
    @cached(key_prefix="orders:pending", ttl=settings.CACHE_TTL_REALTIME)
    async def get_pending_orders_count(db: AsyncSession) -> int:
        """
        Get count of pending orders.

        Args:
            db: Database session

        Returns:
            Count of pending orders
        """
        stmt = select(func.count(Order.id)).where(Order.status == "pending")
        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    @cached(key_prefix="orders:today", ttl=settings.CACHE_TTL_REALTIME)
    async def get_today_orders_stats(db: AsyncSession) -> dict:
        """
        Get order statistics for today.

        Args:
            db: Database session

        Returns:
            Dictionary with today's order stats
        """
        from datetime import datetime

        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())

        stmt = (
            select(
                func.count(Order.id).label("count"),
                func.sum(Order.total_amount).label("revenue"),
                func.avg(Order.total_amount).label("avg_value"),
            )
            .where(Order.order_date >= start_of_day)
            .where(Order.status == "completed")
        )

        result = await db.execute(stmt)
        row = result.one()

        return {
            "orders_count": row.count or 0,
            "total_revenue": row.revenue or Decimal("0.00"),
            "avg_order_value": row.avg_value or Decimal("0.00"),
        }

    @staticmethod
    async def get_customer_orders(
        db: AsyncSession, customer_id: UUID, limit: int = 10
    ) -> list[Order]:
        """
        Get recent orders for a customer.

        Args:
            db: Database session
            customer_id: Customer UUID
            limit: Maximum number of orders to return

        Returns:
            List of orders
        """
        stmt = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())


# Singleton instance
order_service = OrderService()
