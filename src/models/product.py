"""Product model for storing product information and pricing."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .category import Category
    from .order_item import OrderItem


class Product(Base, UUIDMixin, TimestampMixin):
    """Product model for e-commerce catalog.

    Stores product information including pricing, cost, and inventory
    for profitability analysis.
    """

    __tablename__ = "products"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Product name",
    )

    # Category
    category_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Category ID",
    )

    # Pricing
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Cost price (for profit calculations)",
    )

    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        index=True,
        comment="Selling price",
    )

    # Inventory
    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Current stock quantity",
    )

    # Relationships
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
        lazy="selectin",
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "cost_price >= 0",
            name="ck_product_cost_price_positive",
        ),
        CheckConstraint(
            "selling_price >= 0",
            name="ck_product_selling_price_positive",
        ),
        CheckConstraint(
            "stock_quantity >= 0",
            name="ck_product_stock_quantity_positive",
        ),
        Index("idx_products_category", "category_id"),
        Index("idx_products_price", "selling_price"),
        Index("idx_products_stock", "stock_quantity"),
        Index("idx_products_name", "name"),
        {"comment": "Products table for e-commerce catalog"},
    )

    @property
    def profit_margin(self) -> Decimal:
        """Calculate profit margin (selling_price - cost_price)."""
        return self.selling_price - self.cost_price

    @property
    def profit_margin_percentage(self) -> float:
        """Calculate profit margin percentage."""
        if self.selling_price == 0:
            return 0.0
        return float((self.profit_margin / self.selling_price) * 100)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Product(id={self.id}, name={self.name}, price={self.selling_price})>"
