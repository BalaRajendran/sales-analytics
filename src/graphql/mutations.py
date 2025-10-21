"""
GraphQL mutations for the Sales Dashboard API.

All mutations automatically invalidate related caches.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import cache_manager
from src.graphql.types import (
    CreateCustomerInput,
    CreateOrderInput,
    CreateProductInput,
    Customer,
    CustomerMutationResponse,
    MutationResponse,
    Order,
    OrderMutationResponse,
    Product,
    ProductMutationResponse,
    UpdateCustomerInput,
    UpdateOrderStatusInput,
    UpdateProductInput,
)
from src.models.customer import Customer as CustomerModel
from src.models.order import Order as OrderModel
from src.models.order_item import OrderItem as OrderItemModel
from src.models.product import Product as ProductModel
from src.services.cache_invalidation import cache_invalidation_service


@strawberry.type
class Mutation:
    """Root Mutation type for GraphQL API."""

    # ===========================
    # Product Mutations
    # ===========================

    @strawberry.mutation
    async def create_product(
        self, input: CreateProductInput, info: strawberry.Info = None
    ) -> ProductMutationResponse:
        """
        Create a new product.

        Automatically invalidates product and category caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Create product
            product = ProductModel(
                id=uuid4(),
                name=input.name,
                category_id=input.category_id,
                cost_price=input.cost_price,
                selling_price=input.selling_price,
                stock_quantity=input.stock_quantity,
            )

            db.add(product)
            await db.commit()
            await db.refresh(product)

            # Invalidate caches
            await cache_invalidation_service.invalidate_product_cache()
            await cache_invalidation_service.invalidate_category_cache(input.category_id)
            await cache_invalidation_service.invalidate_dashboard_cache()

            return ProductMutationResponse(
                success=True,
                message="Product created successfully",
                product=Product(
                    id=product.id,
                    name=product.name,
                    category_id=product.category_id,
                    cost_price=product.cost_price,
                    selling_price=product.selling_price,
                    stock_quantity=product.stock_quantity,
                    profit_margin=product.profit_margin,
                    profit_margin_percentage=product.profit_margin_percentage,
                    created_at=product.created_at,
                    updated_at=product.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return ProductMutationResponse(
                success=False,
                message="Failed to create product",
                errors=[str(e)],
            )

    @strawberry.mutation
    async def update_product(
        self, product_id: UUID, input: UpdateProductInput, info: strawberry.Info = None
    ) -> ProductMutationResponse:
        """
        Update an existing product.

        Automatically invalidates related caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Get product
            stmt = select(ProductModel).where(ProductModel.id == product_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()

            if not product:
                return ProductMutationResponse(
                    success=False,
                    message="Product not found",
                    errors=["Product with given ID does not exist"],
                )

            # Update fields
            if input.name is not None:
                product.name = input.name
            if input.category_id is not None:
                product.category_id = input.category_id
            if input.cost_price is not None:
                product.cost_price = input.cost_price
            if input.selling_price is not None:
                product.selling_price = input.selling_price
            if input.stock_quantity is not None:
                product.stock_quantity = input.stock_quantity

            await db.commit()
            await db.refresh(product)

            # Invalidate caches
            await cache_invalidation_service.on_product_updated(
                product_id, product.category_id
            )

            return ProductMutationResponse(
                success=True,
                message="Product updated successfully",
                product=Product(
                    id=product.id,
                    name=product.name,
                    category_id=product.category_id,
                    cost_price=product.cost_price,
                    selling_price=product.selling_price,
                    stock_quantity=product.stock_quantity,
                    profit_margin=product.profit_margin,
                    profit_margin_percentage=product.profit_margin_percentage,
                    created_at=product.created_at,
                    updated_at=product.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return ProductMutationResponse(
                success=False,
                message="Failed to update product",
                errors=[str(e)],
            )

    @strawberry.mutation
    async def delete_product(
        self, product_id: UUID, info: strawberry.Info = None
    ) -> MutationResponse:
        """
        Delete a product.

        Automatically invalidates related caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Get product
            stmt = select(ProductModel).where(ProductModel.id == product_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()

            if not product:
                return MutationResponse(
                    success=False,
                    message="Product not found",
                    errors=["Product with given ID does not exist"],
                )

            category_id = product.category_id

            # Delete product
            await db.delete(product)
            await db.commit()

            # Invalidate caches
            await cache_invalidation_service.invalidate_product_cache(product_id)
            await cache_invalidation_service.invalidate_category_cache(category_id)
            await cache_invalidation_service.invalidate_dashboard_cache()

            return MutationResponse(
                success=True,
                message="Product deleted successfully",
            )

        except Exception as e:
            await db.rollback()
            return MutationResponse(
                success=False,
                message="Failed to delete product",
                errors=[str(e)],
            )

    # ===========================
    # Customer Mutations
    # ===========================

    @strawberry.mutation
    async def create_customer(
        self, input: CreateCustomerInput, info: strawberry.Info = None
    ) -> CustomerMutationResponse:
        """
        Create a new customer.

        Automatically invalidates customer caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Check if email already exists
            stmt = select(CustomerModel).where(CustomerModel.email == input.email)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return CustomerMutationResponse(
                    success=False,
                    message="Customer with this email already exists",
                    errors=["Email must be unique"],
                )

            # Create customer
            customer = CustomerModel(
                id=uuid4(),
                name=input.name,
                email=input.email,
                segment=input.segment.value if input.segment else None,
            )

            db.add(customer)
            await db.commit()
            await db.refresh(customer)

            # Invalidate caches
            await cache_invalidation_service.invalidate_customer_cache()
            await cache_invalidation_service.invalidate_dashboard_cache()

            return CustomerMutationResponse(
                success=True,
                message="Customer created successfully",
                customer=Customer(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                    segment=customer.segment,
                    total_lifetime_value=customer.total_lifetime_value,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return CustomerMutationResponse(
                success=False,
                message="Failed to create customer",
                errors=[str(e)],
            )

    @strawberry.mutation
    async def update_customer(
        self, customer_id: UUID, input: UpdateCustomerInput, info: strawberry.Info = None
    ) -> CustomerMutationResponse:
        """
        Update an existing customer.

        Automatically invalidates related caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Get customer
            stmt = select(CustomerModel).where(CustomerModel.id == customer_id)
            result = await db.execute(stmt)
            customer = result.scalar_one_or_none()

            if not customer:
                return CustomerMutationResponse(
                    success=False,
                    message="Customer not found",
                    errors=["Customer with given ID does not exist"],
                )

            # Update fields
            if input.name is not None:
                customer.name = input.name
            if input.email is not None:
                # Check if new email is unique
                email_stmt = (
                    select(CustomerModel)
                    .where(CustomerModel.email == input.email)
                    .where(CustomerModel.id != customer_id)
                )
                email_result = await db.execute(email_stmt)
                if email_result.scalar_one_or_none():
                    return CustomerMutationResponse(
                        success=False,
                        message="Email already in use",
                        errors=["Email must be unique"],
                    )
                customer.email = input.email
            if input.segment is not None:
                customer.segment = input.segment.value
            if input.total_lifetime_value is not None:
                customer.total_lifetime_value = input.total_lifetime_value

            await db.commit()
            await db.refresh(customer)

            # Invalidate caches
            await cache_invalidation_service.on_customer_updated(customer_id)

            return CustomerMutationResponse(
                success=True,
                message="Customer updated successfully",
                customer=Customer(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                    segment=customer.segment,
                    total_lifetime_value=customer.total_lifetime_value,
                    created_at=customer.created_at,
                    updated_at=customer.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return CustomerMutationResponse(
                success=False,
                message="Failed to update customer",
                errors=[str(e)],
            )

    @strawberry.mutation
    async def delete_customer(
        self, customer_id: UUID, info: strawberry.Info = None
    ) -> MutationResponse:
        """
        Delete a customer.

        Note: This will fail if customer has existing orders.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Get customer
            stmt = select(CustomerModel).where(CustomerModel.id == customer_id)
            result = await db.execute(stmt)
            customer = result.scalar_one_or_none()

            if not customer:
                return MutationResponse(
                    success=False,
                    message="Customer not found",
                    errors=["Customer with given ID does not exist"],
                )

            # Check for existing orders
            order_stmt = select(OrderModel).where(OrderModel.customer_id == customer_id).limit(1)
            order_result = await db.execute(order_stmt)
            if order_result.scalar_one_or_none():
                return MutationResponse(
                    success=False,
                    message="Cannot delete customer with existing orders",
                    errors=["Customer has associated orders"],
                )

            # Delete customer
            await db.delete(customer)
            await db.commit()

            # Invalidate caches
            await cache_invalidation_service.invalidate_customer_cache(customer_id)
            await cache_invalidation_service.invalidate_dashboard_cache()

            return MutationResponse(
                success=True,
                message="Customer deleted successfully",
            )

        except Exception as e:
            await db.rollback()
            return MutationResponse(
                success=False,
                message="Failed to delete customer",
                errors=[str(e)],
            )

    # ===========================
    # Order Mutations
    # ===========================

    @strawberry.mutation
    async def create_order(
        self, input: CreateOrderInput, info: strawberry.Info = None
    ) -> OrderMutationResponse:
        """
        Create a new order with items.

        Automatically invalidates related caches and updates customer lifetime value.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Verify customer exists
            customer_stmt = select(CustomerModel).where(CustomerModel.id == input.customer_id)
            customer_result = await db.execute(customer_stmt)
            customer = customer_result.scalar_one_or_none()

            if not customer:
                return OrderMutationResponse(
                    success=False,
                    message="Customer not found",
                    errors=["Customer with given ID does not exist"],
                )

            # Calculate total amount
            total_amount = sum(
                item.unit_price * item.quantity for item in input.items
            )

            # Create order
            order = OrderModel(
                id=uuid4(),
                customer_id=input.customer_id,
                sales_rep_id=input.sales_rep_id,
                order_date=input.order_date,
                total_amount=total_amount,
                status="pending",
            )

            db.add(order)
            await db.flush()  # Get order ID

            # Create order items
            for item_input in input.items:
                order_item = OrderItemModel(
                    id=uuid4(),
                    order_id=order.id,
                    product_id=item_input.product_id,
                    quantity=item_input.quantity,
                    unit_price=item_input.unit_price,
                    total_price=item_input.unit_price * item_input.quantity,
                )
                db.add(order_item)

            await db.commit()
            await db.refresh(order)

            # Update customer lifetime value
            orders_stmt = (
                select(func.sum(OrderModel.total_amount))
                .where(OrderModel.customer_id == input.customer_id)
                .where(OrderModel.status == "completed")
            )
            ltv_result = await db.execute(orders_stmt)
            ltv = ltv_result.scalar() or Decimal("0.00")
            customer.total_lifetime_value = ltv
            await db.commit()

            # Invalidate caches
            await cache_invalidation_service.on_order_created(order.id, input.customer_id)

            return OrderMutationResponse(
                success=True,
                message="Order created successfully",
                order=Order(
                    id=order.id,
                    customer_id=order.customer_id,
                    sales_rep_id=order.sales_rep_id,
                    order_date=order.order_date,
                    total_amount=order.total_amount,
                    status=order.status,
                    profit=order.profit,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return OrderMutationResponse(
                success=False,
                message="Failed to create order",
                errors=[str(e)],
            )

    @strawberry.mutation
    async def update_order_status(
        self, input: UpdateOrderStatusInput, info: strawberry.Info = None
    ) -> OrderMutationResponse:
        """
        Update order status.

        Automatically invalidates related caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Get order
            stmt = select(OrderModel).where(OrderModel.id == input.order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                return OrderMutationResponse(
                    success=False,
                    message="Order not found",
                    errors=["Order with given ID does not exist"],
                )

            old_status = order.status
            order.status = input.status.value

            await db.commit()
            await db.refresh(order)

            # Invalidate caches
            status_changed = old_status != order.status
            await cache_invalidation_service.on_order_updated(
                order.id, order.customer_id, status_changed
            )

            return OrderMutationResponse(
                success=True,
                message=f"Order status updated to {input.status.value}",
                order=Order(
                    id=order.id,
                    customer_id=order.customer_id,
                    sales_rep_id=order.sales_rep_id,
                    order_date=order.order_date,
                    total_amount=order.total_amount,
                    status=order.status,
                    profit=order.profit,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return OrderMutationResponse(
                success=False,
                message="Failed to update order status",
                errors=[str(e)],
            )

    @strawberry.mutation
    async def cancel_order(
        self, order_id: UUID, info: strawberry.Info = None
    ) -> OrderMutationResponse:
        """
        Cancel an order.

        Automatically invalidates related caches.
        """
        db: AsyncSession = info.context["db"]

        try:
            # Get order
            stmt = select(OrderModel).where(OrderModel.id == order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                return OrderMutationResponse(
                    success=False,
                    message="Order not found",
                    errors=["Order with given ID does not exist"],
                )

            if order.status == "completed":
                return OrderMutationResponse(
                    success=False,
                    message="Cannot cancel completed order",
                    errors=["Order is already completed"],
                )

            if order.status == "cancelled":
                return OrderMutationResponse(
                    success=False,
                    message="Order is already cancelled",
                    errors=["Order status is already cancelled"],
                )

            order.status = "cancelled"
            await db.commit()
            await db.refresh(order)

            # Invalidate caches
            await cache_invalidation_service.on_order_updated(order.id, order.customer_id, True)

            return OrderMutationResponse(
                success=True,
                message="Order cancelled successfully",
                order=Order(
                    id=order.id,
                    customer_id=order.customer_id,
                    sales_rep_id=order.sales_rep_id,
                    order_date=order.order_date,
                    total_amount=order.total_amount,
                    status=order.status,
                    profit=order.profit,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                ),
            )

        except Exception as e:
            await db.rollback()
            return OrderMutationResponse(
                success=False,
                message="Failed to cancel order",
                errors=[str(e)],
            )

    # ===========================
    # Cache Management Mutations
    # ===========================

    @strawberry.mutation
    async def clear_cache(
        self, cache_pattern: Optional[str] = None, info: strawberry.Info = None
    ) -> MutationResponse:
        """
        Clear cache by pattern or clear all caches.

        Use with caution!
        """
        try:
            if cache_pattern:
                # Clear specific pattern
                deleted = await cache_manager.delete_pattern(cache_pattern)
                return MutationResponse(
                    success=True,
                    message=f"Cleared {deleted} cache entries matching pattern: {cache_pattern}",
                )
            else:
                # Clear all caches
                await cache_invalidation_service.clear_all_cache()
                return MutationResponse(
                    success=True,
                    message="All caches cleared successfully",
                )

        except Exception as e:
            return MutationResponse(
                success=False,
                message="Failed to clear cache",
                errors=[str(e)],
            )
