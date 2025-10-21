"""
DataLoaders for efficient batch loading in GraphQL.

DataLoaders solve the N+1 query problem by batching and caching requests.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from src.models.category import Category
from src.models.customer import Customer
from src.models.order import Order
from src.models.product import Product
from src.models.sales_rep import SalesRepresentative


class Dataloaders:
    """Container for all dataloaders."""

    def __init__(self, db: AsyncSession):
        self.db = db

        # Initialize all dataloaders
        self.product_loader = DataLoader(load_fn=self._load_products)
        self.category_loader = DataLoader(load_fn=self._load_categories)
        self.customer_loader = DataLoader(load_fn=self._load_customers)
        self.sales_rep_loader = DataLoader(load_fn=self._load_sales_reps)
        self.order_loader = DataLoader(load_fn=self._load_orders)

    async def _load_products(self, product_ids: list[UUID]) -> list[Optional[Product]]:
        """
        Batch load products by IDs.

        Args:
            product_ids: List of product IDs to load

        Returns:
            List of products in the same order as input IDs
        """
        # Fetch all products in one query
        stmt = select(Product).where(Product.id.in_(product_ids))
        result = await self.db.execute(stmt)
        products = result.scalars().all()

        # Create a mapping for quick lookup
        product_map = {product.id: product for product in products}

        # Return products in the same order as requested IDs
        # Use None for missing products
        return [product_map.get(product_id) for product_id in product_ids]

    async def _load_categories(self, category_ids: list[UUID]) -> list[Optional[Category]]:
        """
        Batch load categories by IDs.

        Args:
            category_ids: List of category IDs to load

        Returns:
            List of categories in the same order as input IDs
        """
        stmt = select(Category).where(Category.id.in_(category_ids))
        result = await self.db.execute(stmt)
        categories = result.scalars().all()

        category_map = {category.id: category for category in categories}
        return [category_map.get(category_id) for category_id in category_ids]

    async def _load_customers(self, customer_ids: list[UUID]) -> list[Optional[Customer]]:
        """
        Batch load customers by IDs.

        Args:
            customer_ids: List of customer IDs to load

        Returns:
            List of customers in the same order as input IDs
        """
        stmt = select(Customer).where(Customer.id.in_(customer_ids))
        result = await self.db.execute(stmt)
        customers = result.scalars().all()

        customer_map = {customer.id: customer for customer in customers}
        return [customer_map.get(customer_id) for customer_id in customer_ids]

    async def _load_sales_reps(
        self, sales_rep_ids: list[UUID]
    ) -> list[Optional[SalesRepresentative]]:
        """
        Batch load sales representatives by IDs.

        Args:
            sales_rep_ids: List of sales rep IDs to load

        Returns:
            List of sales reps in the same order as input IDs
        """
        stmt = select(SalesRepresentative).where(SalesRepresentative.id.in_(sales_rep_ids))
        result = await self.db.execute(stmt)
        sales_reps = result.scalars().all()

        sales_rep_map = {sales_rep.id: sales_rep for sales_rep in sales_reps}
        return [sales_rep_map.get(sales_rep_id) for sales_rep_id in sales_rep_ids]

    async def _load_orders(self, order_ids: list[UUID]) -> list[Optional[Order]]:
        """
        Batch load orders by IDs.

        Args:
            order_ids: List of order IDs to load

        Returns:
            List of orders in the same order as input IDs
        """
        stmt = select(Order).where(Order.id.in_(order_ids))
        result = await self.db.execute(stmt)
        orders = result.scalars().all()

        order_map = {order.id: order for order in orders}
        return [order_map.get(order_id) for order_id in order_ids]


def get_dataloaders(db: AsyncSession) -> Dataloaders:
    """
    Create a new dataloaders instance for the request.

    Args:
        db: Database session

    Returns:
        Dataloaders instance
    """
    return Dataloaders(db)
