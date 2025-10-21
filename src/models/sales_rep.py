"""Sales Representative model for tracking sales team performance."""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .order import Order


class SalesRepresentative(Base, UUIDMixin, TimestampMixin):
    """Sales Representative model for team performance tracking.

    Stores sales rep information including region and commission rate
    for performance analytics.
    """

    __tablename__ = "sales_representatives"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Sales representative full name",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Sales representative email address (unique)",
    )

    # Territory
    region: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Sales region or territory",
    )

    # Commission
    commission_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Commission rate percentage (e.g., 5.00 for 5%)",
    )

    # Relationships
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="sales_rep",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "commission_rate >= 0 AND commission_rate <= 100",
            name="ck_sales_rep_commission_rate_range",
        ),
        Index("idx_sales_reps_region", "region"),
        Index("idx_sales_reps_email", "email"),
        {"comment": "Sales representatives table for performance tracking"},
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<SalesRepresentative(id={self.id}, name={self.name}, region={self.region})>"
