"""
Database Seeding Script

Seeds the database with realistic test data:
- 50 categories
- 500 products
- 200 customers
- 50 sales representatives
- 1000 orders with items
"""

import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.category import Category
from src.models.customer import Customer
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.product import Product
from src.models.sales_rep import SalesRepresentative

# Simple name generator (replacing Faker)
FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa", "William", "Emily",
               "James", "Olivia", "Richard", "Sophia", "Thomas", "Isabella", "Daniel", "Mia", "Matthew", "Charlotte"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

def generate_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def generate_email(name, suffix=""):
    base_email = name.lower().replace(' ', '.')
    if suffix:
        return f"{base_email}.{suffix}@example.com"
    return f"{base_email}@example.com"

def generate_word():
    words = ["Ultra", "Pro", "Max", "Plus", "Premium", "Deluxe", "Elite", "Advanced", "Basic", "Standard"]
    return random.choice(words)


# Categories for products
CATEGORIES = [
    "Electronics", "Computers", "Smartphones", "Tablets", "Accessories",
    "Home & Garden", "Furniture", "Kitchen", "Bedding", "Decor",
    "Clothing", "Men's Fashion", "Women's Fashion", "Kids", "Shoes",
    "Sports", "Fitness Equipment", "Outdoor Gear", "Team Sports", "Cycling",
    "Books", "Fiction", "Non-Fiction", "Educational", "Comics",
    "Toys", "Action Figures", "Board Games", "Puzzles", "Educational Toys",
    "Beauty", "Skincare", "Makeup", "Hair Care", "Fragrances",
    "Automotive", "Parts", "Accessories", "Tools", "Maintenance",
    "Health", "Vitamins", "Supplements", "Medical", "Wellness",
    "Office", "Supplies", "Furniture", "Electronics", "Organization",
]

# Product name templates
PRODUCT_TEMPLATES = {
    "Electronics": ["Smart TV", "Bluetooth Speaker", "Headphones", "Camera", "Smartwatch"],
    "Computers": ["Laptop", "Desktop PC", "Monitor", "Keyboard", "Mouse"],
    "Smartphones": ["iPhone", "Galaxy Phone", "Pixel Phone", "OnePlus", "Xiaomi"],
    "Sports": ["Running Shoes", "Yoga Mat", "Dumbbells", "Treadmill", "Bike"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sweater"],
    "default": ["Product", "Item", "Gadget", "Device", "Tool"]
}

# Sales regions
REGIONS = ["North", "South", "East", "West", "Central"]

# Customer segments
SEGMENTS = ["Premium", "Regular", "New", "At-Risk", "Churned"]

# Order statuses
ORDER_STATUSES = ["completed", "pending", "processing", "cancelled"]
STATUS_WEIGHTS = [0.7, 0.15, 0.1, 0.05]  # 70% completed, 15% pending, etc.


async def seed_categories(session: AsyncSession) -> list[Category]:
    """Seed categories."""
    print("Seeding categories...")
    categories = []

    for i, category_name in enumerate(CATEGORIES[:50]):
        category = Category(
            id=uuid4(),
            name=category_name,
            parent_id=None,  # Simplified - no parent categories for now
        )
        categories.append(category)
        session.add(category)

    await session.commit()
    print(f"✓ Created {len(categories)} categories")
    return categories


async def seed_products(session: AsyncSession, categories: list[Category]) -> list[Product]:
    """Seed products."""
    print("Seeding products...")
    products = []

    for i in range(500):
        category = random.choice(categories)

        # Get product template
        templates = PRODUCT_TEMPLATES.get(category.name, PRODUCT_TEMPLATES["default"])
        base_name = random.choice(templates)

        # Generate prices
        cost_price = Decimal(str(round(random.uniform(10, 500), 2)))
        markup = Decimal(str(round(random.uniform(1.2, 2.5), 2)))
        selling_price = cost_price * markup

        product = Product(
            id=uuid4(),
            name=f"{base_name} {generate_word()} {i+1}",
            category_id=category.id,
            cost_price=cost_price,
            selling_price=selling_price,
            stock_quantity=random.randint(0, 500),
        )
        products.append(product)
        session.add(product)

    await session.commit()
    print(f"✓ Created {len(products)} products")
    return products


async def seed_customers(session: AsyncSession) -> list[Customer]:
    """Seed customers."""
    print("Seeding customers...")
    customers = []

    for i in range(200):
        # Random lifetime value based on segment
        segment = random.choice(SEGMENTS)
        if segment == "Premium":
            ltv = Decimal(str(round(random.uniform(5000, 50000), 2)))
        elif segment == "Regular":
            ltv = Decimal(str(round(random.uniform(1000, 5000), 2)))
        elif segment == "New":
            ltv = Decimal(str(round(random.uniform(100, 1000), 2)))
        elif segment == "At-Risk":
            ltv = Decimal(str(round(random.uniform(500, 3000), 2)))
        else:  # Churned
            ltv = Decimal(str(round(random.uniform(0, 500), 2)))

        name = generate_name()
        customer = Customer(
            id=uuid4(),
            name=name,
            email=generate_email(name, str(i)),  # Add index to make email unique
            segment=segment,
            total_lifetime_value=ltv,
        )
        customers.append(customer)
        session.add(customer)

    await session.commit()
    print(f"✓ Created {len(customers)} customers")
    return customers


async def seed_sales_reps(session: AsyncSession) -> list[SalesRepresentative]:
    """Seed sales representatives."""
    print("Seeding sales representatives...")
    sales_reps = []

    for i in range(50):
        name = generate_name()
        sales_rep = SalesRepresentative(
            id=uuid4(),
            name=name,
            email=generate_email(name, f"rep{i}"),  # Add unique email
            region=random.choice(REGIONS),
            commission_rate=Decimal(str(round(random.uniform(5, 15), 2))),
        )
        sales_reps.append(sales_rep)
        session.add(sales_rep)

    await session.commit()
    print(f"✓ Created {len(sales_reps)} sales representatives")
    return sales_reps


async def seed_orders(
    session: AsyncSession,
    customers: list[Customer],
    sales_reps: list[SalesRepresentative],
    products: list[Product],
) -> None:
    """Seed orders and order items."""
    print("Seeding orders and order items...")

    # Generate orders over the last 90 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)

    orders_created = 0
    items_created = 0

    for i in range(1000):
        # Random order date within the last 90 days
        days_ago = random.randint(0, 90)
        order_date = end_date - timedelta(days=days_ago)

        customer = random.choice(customers)
        sales_rep = random.choice(sales_reps)
        status = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0]

        # Create order
        order = Order(
            id=uuid4(),
            customer_id=customer.id,
            sales_rep_id=sales_rep.id,
            order_date=order_date,
            status=status,
            total_amount=Decimal("0.00"),
        )
        session.add(order)
        orders_created += 1

        # Add 1-5 items per order
        num_items = random.randint(1, 5)
        order_total = Decimal("0.00")

        for _ in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 10)

            item_total = product.selling_price * quantity

            order_item = OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.selling_price,
                total_price=item_total,
            )
            session.add(order_item)
            items_created += 1

            order_total += item_total

        # Update order total (profit is computed automatically)
        order.total_amount = order_total

        # Commit in batches of 100 orders
        if (i + 1) % 100 == 0:
            await session.commit()
            print(f"  Progress: {i + 1}/1000 orders created...")

    await session.commit()
    print(f"✓ Created {orders_created} orders with {items_created} items")


async def clear_database(session: AsyncSession) -> None:
    """Clear all existing data."""
    print("Clearing existing data...")

    # Delete in correct order due to foreign keys
    await session.execute(text("DELETE FROM order_items"))
    await session.execute(text("DELETE FROM orders"))
    await session.execute(text("DELETE FROM products"))
    await session.execute(text("DELETE FROM categories"))
    await session.execute(text("DELETE FROM customers"))
    await session.execute(text("DELETE FROM sales_representatives"))

    await session.commit()
    print("✓ Database cleared")


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("Starting database seeding...")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        # Clear existing data
        await clear_database(session)

        # Seed data in order
        categories = await seed_categories(session)
        products = await seed_products(session, categories)
        customers = await seed_customers(session)
        sales_reps = await seed_sales_reps(session)
        await seed_orders(session, customers, sales_reps, products)

    print("=" * 60)
    print("✓ Database seeding completed successfully!")
    print("=" * 60)
    print("\nSummary:")
    print("  - 50 categories")
    print("  - 500 products")
    print("  - 200 customers")
    print("  - 50 sales representatives")
    print("  - 1000 orders with ~3000 items")
    print("\nYou can now view the data in the dashboard!")


if __name__ == "__main__":
    asyncio.run(main())
