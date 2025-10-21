"""Customer model for storing customer information and segments."""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .order import Order


class Customer(Base, UUIDMixin, TimestampMixin):
    """Customer model for e-commerce analytics.

    Stores customer information including segment classification
    and lifetime value for analytics purposes.
    """

    __tablename__ = "customers"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Customer full name",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Customer email address (unique)",
    )

    # Segmentation
    segment: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Customer segment: Premium, Regular, New, At-Risk, Churned",
    )

    # Analytics
    total_lifetime_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        index=True,
        comment="Total lifetime value of customer",
    )

    # Relationships
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="customer",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "segment IN ('Premium', 'Regular', 'New', 'At-Risk', 'Churned')",
            name="ck_customer_segment",
        ),
        CheckConstraint(
            "total_lifetime_value >= 0",
            name="ck_customer_lifetime_value_positive",
        ),
        Index("idx_customers_segment", "segment"),
        Index("idx_customers_email", "email"),
        Index("idx_customers_created_at", "created_at"),
        Index("idx_customers_lifetime_value", "total_lifetime_value"),
        {"comment": "Customers table for e-commerce analytics"},
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Customer(id={self.id}, email={self.email}, segment={self.segment})>"
