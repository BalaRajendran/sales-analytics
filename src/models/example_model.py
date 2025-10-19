"""
Example Model Template.

This is a template file showing the pattern for creating database models.
Replace this with your actual sales dashboard models (e.g., Sale, Product, Customer, etc.)
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


# Example Model Template - Replace with your actual models
class ExampleModel(Base):
    """
    Example model template.

    Replace this with your actual sales dashboard models like:
    - Sale
    - Product
    - Customer
    - Order
    - Revenue
    etc.
    """

    __tablename__ = "example_models"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Example fields - customize based on your needs
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps - typically used in most models
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ExampleModel(id={self.id}, name={self.name})>"
