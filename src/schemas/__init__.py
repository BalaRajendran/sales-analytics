"""
Pydantic schemas.

Import your sales dashboard schemas here.
Example:
    from src.schemas.sale import SaleCreate, SaleResponse
    from src.schemas.product import ProductCreate, ProductResponse

    __all__ = ["SaleCreate", "SaleResponse", "ProductCreate", "ProductResponse"]
"""

from src.schemas.example_schema import ExampleCreate, ExampleResponse, ExampleUpdate

__all__ = ["ExampleCreate", "ExampleResponse", "ExampleUpdate"]
