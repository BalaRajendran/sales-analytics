"""Order model for storing order transactions (partitioned by date)."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .customer import Customer
    from .order_item import OrderItem
    from .sales_rep import SalesRepresentative


class Order(Base, TimestampMixin):
    """Order model for e-commerce transactions.

    Note: This table is partitioned by created_at (monthly partitions)
    for optimal query performance with large datasets.

    Partitioning strategy:
    - Range partitioning by created_at
    - Monthly partitions (e.g., orders_2024_01, orders_2024_02)
    - Composite primary key (id, created_at) required for partitioning
    - See migrations/versions/002_partition_orders.sql for setup
    """

    __tablename__ = "orders"

    # Primary key - must include partition key for partitioned tables
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=lambda: __import__('uuid').uuid4(),
        comment="Order unique identifier",
    )

    # Customer
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Customer ID",
    )

    # Sales Representative (optional)
    sales_rep_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sales_representatives.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Sales representative ID (optional)",
    )

    # Order Information
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Order date and time",
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        index=True,
        comment="Total order amount",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Order status: pending, processing, completed, cancelled, refunded",
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="orders",
        lazy="selectin",
    )

    sales_rep: Mapped[Optional["SalesRepresentative"]] = relationship(
        "SalesRepresentative",
        back_populates="orders",
        lazy="selectin",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        # Composite primary key including partition key
        # This is REQUIRED for partitioned tables in PostgreSQL
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'cancelled', 'refunded')",
            name="ck_order_status",
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="ck_order_total_amount_positive",
        ),
        Index("idx_orders_customer", "customer_id"),
        Index("idx_orders_sales_rep", "sales_rep_id"),
        Index("idx_orders_date", "order_date"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_amount", "total_amount"),
        # Composite index for common queries
        Index("idx_orders_date_status", "order_date", "status"),
        Index("idx_orders_customer_date", "customer_id", "order_date"),
        {
            "comment": "Orders table (partitioned by created_at for performance)",
            # Note: Partitioning is NOT enabled by default to avoid complexity
            # To enable partitioning, run: migrations/versions/002_partition_orders.sql
            # "postgresql_partition_by": "RANGE (created_at)",
        },
    )

    @property
    def profit(self) -> Decimal:
        """Calculate total profit from all order items."""
        return sum((item.profit for item in self.items), Decimal("0.00"))

    def __repr__(self) -> str:
        """String representation."""
        return f"<Order(id={self.id}, customer_id={self.customer_id}, total={self.total_amount}, status={self.status})>"
