-- Sales Analytics Database Indexes
-- This file creates all necessary indexes for optimal query performance
-- Run this after the initial Alembic migration

-- ========================================
-- Customer Indexes
-- ========================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_segment
    ON customers(segment) WHERE segment IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_email
    ON customers(email);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_created_at
    ON customers(created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_lifetime_value
    ON customers(total_lifetime_value DESC NULLS LAST)
    WHERE total_lifetime_value IS NOT NULL;

-- ========================================
-- Category Indexes
-- ========================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_parent
    ON categories(parent_id) WHERE parent_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_name
    ON categories(name);

-- ========================================
-- Product Indexes
-- ========================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_category
    ON products(category_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_selling_price
    ON products(selling_price);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_stock_low
    ON products(stock_quantity) WHERE stock_quantity < 10;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_name
    ON products(name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_profit_margin
    ON products((selling_price - cost_price) DESC);

-- ========================================
-- Sales Representative Indexes
-- ========================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_reps_region
    ON sales_representatives(region) WHERE region IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_reps_email
    ON sales_representatives(email);

-- ========================================
-- Order Indexes (critical for analytics)
-- ========================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer
    ON orders(customer_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_sales_rep
    ON orders(sales_rep_id) WHERE sales_rep_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_order_date
    ON orders(order_date DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
    ON orders(status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_total_amount
    ON orders(total_amount);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at
    ON orders(created_at DESC);

-- Composite indexes for common query patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_date_status
    ON orders(order_date DESC, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_date
    ON orders(customer_id, order_date DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status_completed
    ON orders(order_date DESC) WHERE status = 'completed';

-- ========================================
-- Order Items Indexes
-- ========================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_order
    ON order_items(order_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_product
    ON order_items(product_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_product_created
    ON order_items(product_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_created_at
    ON order_items(created_at DESC);

-- ========================================
-- Update Table Statistics
-- ========================================

ANALYZE customers;
ANALYZE categories;
ANALYZE products;
ANALYZE sales_representatives;
ANALYZE orders;
ANALYZE order_items;

-- ========================================
-- Grant Permissions (adjust as needed)
-- ========================================

-- Create a read-only role for analytics queries
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analytics_readonly') THEN
        CREATE ROLE analytics_readonly;
    END IF;
END
$$;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
GRANT USAGE ON SCHEMA public TO analytics_readonly;

-- ========================================
-- Index Creation Summary
-- ========================================

SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size((schemaname || '.' || indexname)::regclass)) as index_size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

COMMENT ON TABLE customers IS 'Customers with segmentation and lifetime value tracking';
COMMENT ON TABLE categories IS 'Product categories with hierarchical structure';
COMMENT ON TABLE products IS 'Product catalog with pricing and inventory';
COMMENT ON TABLE sales_representatives IS 'Sales team members with regions and commission rates';
COMMENT ON TABLE orders IS 'Customer orders (partitioned by created_at for performance)';
COMMENT ON TABLE order_items IS 'Line items within orders';
