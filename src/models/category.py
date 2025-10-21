"""Category model for product categorization."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .product import Product


class Category(Base, UUIDMixin, TimestampMixin):
    """Product category model for hierarchical categorization.

    Supports parent-child relationships for nested categories.
    Example: Electronics > Computers > Laptops
    """

    __tablename__ = "categories"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Category name",
    )

    # Hierarchical Structure
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Parent category ID for hierarchical structure",
    )

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
        lazy="selectin",
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Table constraints
    __table_args__ = (
        Index("idx_categories_parent", "parent_id"),
        Index("idx_categories_name", "name"),
        {"comment": "Product categories with hierarchical structure"},
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Category(id={self.id}, name={self.name})>"
