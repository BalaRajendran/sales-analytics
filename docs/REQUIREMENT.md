🎯 Use Case Overview: Sales Analytics Dashboard 
Scenario

You’re building a dashboard for an e-commerce company (say, “ShopX”) that sells multiple product categories online across different regions.
The goal is to analyze sales performance, customer behavior, and product trends.

🧩 Core Entities (Database Tables)

Here’s a normalized relational schema (can be used in PostgreSQL, MySQL, or even a cloud DB like BigQuery).

1. Customers
Column	Type	Description
customer_id	UUID / INT	Primary key
name	VARCHAR	Customer name
email	VARCHAR	Unique email
gender	VARCHAR(10)	Male / Female / Other
age	INT	Customer age
region	VARCHAR(50)	Region or city
created_at	TIMESTAMP	Account creation date
2. Products
Column	Type	Description
product_id	UUID / INT	Primary key
product_name	VARCHAR	Product name
category_id	INT	FK → categories.category_id
price	DECIMAL(10,2)	Base price
cost	DECIMAL(10,2)	Cost price
brand	VARCHAR(50)	Brand name
created_at	TIMESTAMP	When added to catalog
3. Categories
Column	Type	Description
category_id	INT	Primary key
category_name	VARCHAR	e.g., Electronics, Apparel, Groceries
4. Orders
Column	Type	Description
order_id	UUID / INT	Primary key
customer_id	INT	FK → customers.customer_id
order_date	TIMESTAMP	Order timestamp
order_status	VARCHAR	e.g., Completed, Cancelled, Returned
payment_mode	VARCHAR	e.g., Credit Card, UPI, COD
total_amount	DECIMAL(10,2)	Total order amount
discount_amount	DECIMAL(10,2)	Discount applied
5. OrderItems
Column	Type	Description
order_item_id	INT	Primary key
order_id	INT	FK → orders.order_id
product_id	INT	FK → products.product_id
quantity	INT	Quantity ordered
unit_price	DECIMAL(10,2)	Selling price per unit
subtotal	DECIMAL(10,2)	quantity * unit_price
6. Sales Representatives (Optional)
Column	Type	Description
sales_rep_id	INT	Primary key
name	VARCHAR	Rep name
region	VARCHAR	Responsible region
joined_date	DATE	Joining date

Each order can optionally be linked to a sales_rep_id if it’s a B2B order.

📊 Key Analytics to Build in the Dashboard
1. Sales Overview

Total Revenue, Total Orders, Average Order Value

Sales Trend over Time (daily, weekly, monthly)

Top 5 Categories by Revenue

Sales by Payment Mode

2. Product Insights

Top-Selling Products

Low Margin Products (price - cost)

Category Performance Comparison

Inventory Turnover (if you extend schema later)

3. Customer Analytics

New vs Returning Customers

Customer Lifetime Value (CLV)

Sales by Region / Demographics

Repeat Purchase Rate

4. Profitability Metrics

Gross Profit = Σ(unit_price - cost) × quantity

Margin % per Category or Brand

Discount vs Revenue Correlation

🧾 Example Queries
1. Monthly Revenue
SELECT DATE_TRUNC('month', order_date) AS month, 
       SUM(total_amount - discount_amount) AS revenue
FROM orders
WHERE order_status = 'Completed'
GROUP BY 1
ORDER BY 1;

2. Top 5 Products by Sales
SELECT p.product_name, SUM(oi.quantity * oi.unit_price) AS total_sales
FROM orderitems oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 5;

3. Region-Wise Sales
SELECT c.region, SUM(o.total_amount) AS total_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region;
