"""Database models for ShopX Sales Analytics Dashboard.

This module exports all database models for the sales analytics system.
Models include:
- Base: Base model with common mixins
- Customer: Customer information and segmentation
- Category: Product categories with hierarchical structure
- Product: Product catalog with pricing
- SalesRepresentative: Sales team information
- Order: Order transactions (partitioned by date)
- OrderItem: Line items within orders
"""

from .base import Base, TimestampMixin, UUIDMixin
from .category import Category
from .customer import Customer
from .order import Order
from .order_item import OrderItem
from .product import Product
from .sales_rep import SalesRepresentative

__all__ = [
    # Base classes
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # Business models
    "Customer",
    "Category",
    "Product",
    "SalesRepresentative",
    "Order",
    "OrderItem",
]
