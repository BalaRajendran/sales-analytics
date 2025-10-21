"""Order Item model for storing individual items within orders."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .order import Order
    from .product import Product


class OrderItem(Base, UUIDMixin, TimestampMixin):
    """Order Item model for line items in orders.

    Each order can have multiple order items, representing
    different products and quantities.
    """

    __tablename__ = "order_items"

    # Order Reference
    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Order ID",
    )

    # Product Reference
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Product ID",
    )

    # Quantity
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity ordered",
    )

    # Pricing (snapshot at time of order)
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Unit price at time of order",
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        comment="Total price (quantity * unit_price)",
    )

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
        lazy="selectin",
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="order_items",
        lazy="selectin",
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_item_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_order_item_unit_price_positive",
        ),
        CheckConstraint(
            "total_price >= 0",
            name="ck_order_item_total_price_positive",
        ),
        Index("idx_order_items_order", "order_id"),
        Index("idx_order_items_product", "product_id"),
        Index("idx_order_items_product_created", "product_id", "created_at"),
        {"comment": "Order items (line items) for orders"},
    )

    @property
    def profit(self) -> Decimal:
        """Calculate profit for this order item.

        Profit = (selling_price - cost_price) * quantity
        Note: We use the product's current cost_price, not a snapshot.
        In a real system, you might want to store cost_price at time of order.
        """
        if self.product:
            profit_per_unit = self.unit_price - self.product.cost_price
            return profit_per_unit * self.quantity
        return Decimal("0.00")

    def __repr__(self) -> str:
        """String representation."""
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"
