"""
Product service for product operations.

Handles all product CRUD operations with cache management.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache_decorators import cached
from src.core.config import settings
from src.models.product import Product
from src.services.cache_invalidation import cache_invalidation_service


class ProductService:
    """Service for product operations."""

    @staticmethod
    @cached(key_prefix="product:detail", ttl=settings.CACHE_TTL_PRODUCTS)
    async def get_product_by_id(db: AsyncSession, product_id: UUID) -> Optional[Product]:
        """
        Get a product by ID.

        Args:
            db: Database session
            product_id: Product UUID

        Returns:
            Product or None if not found
        """
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_products(
        db: AsyncSession,
        category_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        in_stock: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Product], int]:
        """
        Get paginated list of products with filters.

        Args:
            db: Database session
            category_id: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            in_stock: Filter by stock availability
            search: Search in product name
            limit: Page size
            offset: Page offset

        Returns:
            Tuple of (products list, total count)
        """
        # Build query
        stmt = select(Product)

        # Apply filters
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(Product.selling_price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.selling_price <= max_price)
        if in_stock is not None:
            if in_stock:
                stmt = stmt.where(Product.stock_quantity > 0)
            else:
                stmt = stmt.where(Product.stock_quantity == 0)
        if search:
            stmt = stmt.where(Product.name.ilike(f"%{search}%"))

        # Get total count
        from sqlalchemy import func

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination and execute
        stmt = stmt.limit(limit).offset(offset).order_by(Product.name)
        result = await db.execute(stmt)
        products = result.scalars().all()

        return list(products), total_count

    @staticmethod
    async def create_product(
        db: AsyncSession,
        name: str,
        category_id: UUID,
        cost_price: Decimal,
        selling_price: Decimal,
        stock_quantity: int = 0,
    ) -> Product:
        """
        Create a new product.

        Args:
            db: Database session
            name: Product name
            category_id: Category UUID
            cost_price: Cost price
            selling_price: Selling price
            stock_quantity: Initial stock quantity

        Returns:
            Created product

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if cost_price < 0:
            raise ValueError("Cost price cannot be negative")
        if selling_price < 0:
            raise ValueError("Selling price cannot be negative")
        if stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if selling_price < cost_price:
            raise ValueError("Selling price should be greater than or equal to cost price")

        # Create product
        product = Product(
            id=uuid4(),
            name=name,
            category_id=category_id,
            cost_price=cost_price,
            selling_price=selling_price,
            stock_quantity=stock_quantity,
        )

        db.add(product)
        await db.commit()
        await db.refresh(product)

        # Invalidate caches
        await cache_invalidation_service.invalidate_product_cache()
        await cache_invalidation_service.invalidate_category_cache(category_id)
        await cache_invalidation_service.invalidate_dashboard_cache()

        return product

    @staticmethod
    async def update_product(
        db: AsyncSession,
        product_id: UUID,
        name: Optional[str] = None,
        category_id: Optional[UUID] = None,
        cost_price: Optional[Decimal] = None,
        selling_price: Optional[Decimal] = None,
        stock_quantity: Optional[int] = None,
    ) -> Optional[Product]:
        """
        Update a product.

        Args:
            db: Database session
            product_id: Product UUID
            name: New name (optional)
            category_id: New category (optional)
            cost_price: New cost price (optional)
            selling_price: New selling price (optional)
            stock_quantity: New stock quantity (optional)

        Returns:
            Updated product or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Get product
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            return None

        # Validation
        new_cost = cost_price if cost_price is not None else product.cost_price
        new_selling = selling_price if selling_price is not None else product.selling_price

        if new_cost < 0:
            raise ValueError("Cost price cannot be negative")
        if new_selling < 0:
            raise ValueError("Selling price cannot be negative")
        if stock_quantity is not None and stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if new_selling < new_cost:
            raise ValueError("Selling price should be greater than or equal to cost price")

        # Update fields
        if name is not None:
            product.name = name
        if category_id is not None:
            product.category_id = category_id
        if cost_price is not None:
            product.cost_price = cost_price
        if selling_price is not None:
            product.selling_price = selling_price
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity

        await db.commit()
        await db.refresh(product)

        # Invalidate caches
        await cache_invalidation_service.on_product_updated(product_id, product.category_id)

        return product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: UUID) -> bool:
        """
        Delete a product.

        Args:
            db: Database session
            product_id: Product UUID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If product has associated orders
        """
        # Get product
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            return False

        # Check for associated order items
        from src.models.order_item import OrderItem

        check_stmt = select(OrderItem).where(OrderItem.product_id == product_id).limit(1)
        check_result = await db.execute(check_stmt)
        if check_result.scalar_one_or_none():
            raise ValueError("Cannot delete product with existing orders")

        category_id = product.category_id

        # Delete product
        await db.delete(product)
        await db.commit()

        # Invalidate caches
        await cache_invalidation_service.invalidate_product_cache(product_id)
        await cache_invalidation_service.invalidate_category_cache(category_id)
        await cache_invalidation_service.invalidate_dashboard_cache()

        return True

    @staticmethod
    async def adjust_stock(
        db: AsyncSession, product_id: UUID, quantity_change: int
    ) -> Optional[Product]:
        """
        Adjust product stock quantity.

        Args:
            db: Database session
            product_id: Product UUID
            quantity_change: Amount to add (positive) or subtract (negative)

        Returns:
            Updated product or None if not found

        Raises:
            ValueError: If resulting stock would be negative
        """
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            return None

        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock. Available: {product.stock_quantity}, "
                f"Requested: {abs(quantity_change)}"
            )

        product.stock_quantity = new_quantity
        await db.commit()
        await db.refresh(product)

        # Invalidate caches
        await cache_invalidation_service.invalidate_product_cache(product_id)

        return product

    @staticmethod
    async def get_low_stock_products(
        db: AsyncSession, threshold: int = 10, limit: int = 50
    ) -> list[Product]:
        """
        Get products with low stock.

        Args:
            db: Database session
            threshold: Stock quantity threshold
            limit: Maximum number of products to return

        Returns:
            List of low-stock products
        """
        stmt = (
            select(Product)
            .where(Product.stock_quantity <= threshold)
            .order_by(Product.stock_quantity)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_out_of_stock_products(db: AsyncSession, limit: int = 50) -> list[Product]:
        """
        Get out-of-stock products.

        Args:
            db: Database session
            limit: Maximum number of products to return

        Returns:
            List of out-of-stock products
        """
        stmt = (
            select(Product)
            .where(Product.stock_quantity == 0)
            .order_by(Product.name)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    @cached(key_prefix="product:high_margin", ttl=settings.CACHE_TTL_PRODUCTS)
    async def get_high_margin_products(
        db: AsyncSession, min_margin_percentage: float = 30.0, limit: int = 50
    ) -> list[Product]:
        """
        Get products with high profit margins.

        Args:
            db: Database session
            min_margin_percentage: Minimum profit margin percentage
            limit: Maximum number of products to return

        Returns:
            List of high-margin products
        """
        stmt = select(Product).limit(limit)

        result = await db.execute(stmt)
        products = result.scalars().all()

        # Filter by margin percentage (calculated property)
        high_margin = [
            p for p in products if p.profit_margin_percentage >= min_margin_percentage
        ]

        # Sort by margin percentage (descending)
        high_margin.sort(key=lambda p: p.profit_margin_percentage, reverse=True)

        return high_margin[:limit]

    @staticmethod
    async def bulk_update_prices(
        db: AsyncSession, price_adjustments: list[dict]
    ) -> list[Product]:
        """
        Bulk update product prices.

        Args:
            db: Database session
            price_adjustments: List of dicts with 'product_id', 'cost_price', 'selling_price'

        Returns:
            List of updated products

        Raises:
            ValueError: If any validation fails
        """
        updated_products = []

        for adjustment in price_adjustments:
            product_id = adjustment["product_id"]
            cost_price = adjustment.get("cost_price")
            selling_price = adjustment.get("selling_price")

            product = await ProductService.update_product(
                db=db,
                product_id=product_id,
                cost_price=cost_price,
                selling_price=selling_price,
            )

            if product:
                updated_products.append(product)

        return updated_products


# Singleton instance
product_service = ProductService()
