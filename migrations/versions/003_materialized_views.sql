-- Materialized Views for Analytics Performance
-- These views pre-compute expensive aggregations for fast dashboard queries
-- Run this after initial data load

-- ========================================
-- 1. Daily Sales Summary
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_sales AS
SELECT
    DATE(o.order_date) as sale_date,
    COUNT(DISTINCT o.id) as order_count,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    COUNT(DISTINCT o.sales_rep_id) as active_sales_reps,
    SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) as completed_revenue,
    SUM(CASE WHEN o.status = 'cancelled' THEN o.total_amount ELSE 0 END) as cancelled_revenue,
    SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
    SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders
FROM orders o
WHERE o.order_date >= CURRENT_DATE - INTERVAL '2 years'  -- Keep 2 years of data
GROUP BY DATE(o.order_date);

CREATE UNIQUE INDEX idx_mv_daily_sales_date ON mv_daily_sales(sale_date DESC);

-- ========================================
-- 2. Product Performance Summary
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_product_performance AS
SELECT
    p.id as product_id,
    p.name as product_name,
    p.category_id,
    c.name as category_name,
    p.cost_price,
    p.selling_price,
    p.stock_quantity,
    COUNT(DISTINCT oi.id) as times_sold,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_selling_price,
    SUM(oi.total_price - (p.cost_price * oi.quantity)) as total_profit,
    CASE
        WHEN SUM(oi.total_price) > 0
        THEN (SUM(oi.total_price - (p.cost_price * oi.quantity)) / SUM(oi.total_price) * 100)
        ELSE 0
    END as profit_margin_pct,
    MAX(o.order_date) as last_sold_date,
    MIN(o.order_date) as first_sold_date,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
GROUP BY p.id, p.name, p.category_id, c.name, p.cost_price, p.selling_price, p.stock_quantity;

CREATE UNIQUE INDEX idx_mv_product_perf_id ON mv_product_performance(product_id);
CREATE INDEX IF NOT EXISTS idx_mv_product_perf_revenue ON mv_product_performance(total_revenue DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_mv_product_perf_profit ON mv_product_performance(total_profit DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_mv_product_perf_category ON mv_product_performance(category_id);
CREATE INDEX IF NOT EXISTS idx_mv_product_perf_quantity ON mv_product_performance(total_quantity_sold DESC NULLS LAST);

-- ========================================
-- 3. Customer Segments and RFM Analysis
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_customer_segments AS
SELECT
    c.id as customer_id,
    c.name,
    c.email,
    c.segment,
    COUNT(DISTINCT o.id) as order_count,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    MIN(o.order_date) as first_order_date,
    EXTRACT(DAY FROM (MAX(o.order_date) - MIN(o.order_date))) as customer_lifetime_days,
    CASE
        WHEN COUNT(DISTINCT o.id) > 1
        THEN EXTRACT(DAY FROM (MAX(o.order_date) - MIN(o.order_date))) / (COUNT(DISTINCT o.id) - 1)::float
        ELSE NULL
    END as avg_days_between_orders,
    -- RFM (Recency, Frequency, Monetary) Analysis
    EXTRACT(DAY FROM (CURRENT_DATE - MAX(o.order_date))) as recency_days,
    COUNT(DISTINCT o.id) as frequency,
    SUM(o.total_amount) as monetary_value,
    -- RFM Scores (1-5, with 5 being best)
    CASE
        WHEN EXTRACT(DAY FROM (CURRENT_DATE - MAX(o.order_date))) <= 30 THEN 5
        WHEN EXTRACT(DAY FROM (CURRENT_DATE - MAX(o.order_date))) <= 60 THEN 4
        WHEN EXTRACT(DAY FROM (CURRENT_DATE - MAX(o.order_date))) <= 90 THEN 3
        WHEN EXTRACT(DAY FROM (CURRENT_DATE - MAX(o.order_date))) <= 180 THEN 2
        ELSE 1
    END as recency_score,
    CASE
        WHEN COUNT(DISTINCT o.id) >= 10 THEN 5
        WHEN COUNT(DISTINCT o.id) >= 7 THEN 4
        WHEN COUNT(DISTINCT o.id) >= 4 THEN 3
        WHEN COUNT(DISTINCT o.id) >= 2 THEN 2
        ELSE 1
    END as frequency_score,
    CASE
        WHEN SUM(o.total_amount) >= 10000 THEN 5
        WHEN SUM(o.total_amount) >= 5000 THEN 4
        WHEN SUM(o.total_amount) >= 2000 THEN 3
        WHEN SUM(o.total_amount) >= 500 THEN 2
        ELSE 1
    END as monetary_score
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
GROUP BY c.id, c.name, c.email, c.segment;

CREATE UNIQUE INDEX idx_mv_customer_seg_id ON mv_customer_segments(customer_id);
CREATE INDEX IF NOT EXISTS idx_mv_customer_seg_spent ON mv_customer_segments(total_spent DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_mv_customer_seg_segment ON mv_customer_segments(segment);
CREATE INDEX IF NOT EXISTS idx_mv_customer_seg_recency ON mv_customer_segments(recency_days);
CREATE INDEX IF NOT EXISTS idx_mv_customer_seg_rfm ON mv_customer_segments(recency_score, frequency_score, monetary_score);

-- ========================================
-- 4. Category Performance
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_category_performance AS
SELECT
    c.id as category_id,
    c.name as category_name,
    c.parent_id,
    COUNT(DISTINCT p.id) as product_count,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_price,
    SUM(oi.total_price - (p.cost_price * oi.quantity)) as total_profit,
    CASE
        WHEN SUM(oi.total_price) > 0
        THEN (SUM(oi.total_price - (p.cost_price * oi.quantity)) / SUM(oi.total_price) * 100)
        ELSE 0
    END as profit_margin_pct
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
GROUP BY c.id, c.name, c.parent_id;

CREATE UNIQUE INDEX idx_mv_category_perf_id ON mv_category_performance(category_id);
CREATE INDEX IF NOT EXISTS idx_mv_category_perf_revenue ON mv_category_performance(total_revenue DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_mv_category_perf_profit ON mv_category_performance(total_profit DESC NULLS LAST);

-- ========================================
-- 5. Sales Representative Performance
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_sales_rep_performance AS
SELECT
    sr.id as sales_rep_id,
    sr.name as sales_rep_name,
    sr.region,
    sr.commission_rate,
    COUNT(DISTINCT o.id) as total_orders,
    SUM(o.total_amount) as total_sales,
    AVG(o.total_amount) as avg_order_value,
    SUM(o.total_amount * COALESCE(sr.commission_rate, 0) / 100) as total_commission_earned,
    COUNT(DISTINCT o.customer_id) as unique_customers_served,
    MAX(o.order_date) as last_sale_date,
    MIN(o.order_date) as first_sale_date
FROM sales_representatives sr
LEFT JOIN orders o ON sr.id = o.sales_rep_id AND o.status = 'completed'
GROUP BY sr.id, sr.name, sr.region, sr.commission_rate;

CREATE UNIQUE INDEX idx_mv_sales_rep_perf_id ON mv_sales_rep_performance(sales_rep_id);
CREATE INDEX IF NOT EXISTS idx_mv_sales_rep_perf_sales ON mv_sales_rep_performance(total_sales DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_mv_sales_rep_perf_region ON mv_sales_rep_performance(region);

-- ========================================
-- 6. Hourly Metrics (Last 7 Days)
-- ========================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_metrics AS
SELECT
    date_trunc('hour', o.order_date) as metric_hour,
    COUNT(DISTINCT o.id) as order_count,
    SUM(o.total_amount) as revenue,
    AVG(o.total_amount) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
WHERE o.order_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
AND o.status = 'completed'
GROUP BY date_trunc('hour', o.order_date);

CREATE UNIQUE INDEX idx_mv_hourly_metrics_hour ON mv_hourly_metrics(metric_hour DESC);

-- ========================================
-- Refresh Function for All Materialized Views
-- ========================================

CREATE OR REPLACE FUNCTION refresh_all_analytics_mv()
RETURNS void AS $$
BEGIN
    -- Refresh all materialized views concurrently
    -- Note: CONCURRENTLY allows queries to continue during refresh
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_segments;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_rep_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_metrics;

    RAISE NOTICE 'All materialized views refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Selective Refresh Functions
-- ========================================

CREATE OR REPLACE FUNCTION refresh_realtime_mv()
RETURNS void AS $$
BEGIN
    -- Refresh only frequently-changing views (for realtime dashboard)
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_metrics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_daily_mv()
RETURNS void AS $$
BEGIN
    -- Refresh less frequently-changing views (daily job)
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_segments;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_rep_performance;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Schedule Automatic Refresh (via pg_cron or external scheduler)
-- ========================================

-- Example with pg_cron extension:
/*
-- Refresh realtime views every 15 minutes
SELECT cron.schedule(
    'refresh-realtime-views',
    '*/15 * * * *',
    'SELECT refresh_realtime_mv();'
);

-- Refresh daily views at 2 AM
SELECT cron.schedule(
    'refresh-daily-views',
    '0 2 * * *',
    'SELECT refresh_daily_mv();'
);
*/

-- ========================================
-- Initial Refresh
-- ========================================

SELECT refresh_all_analytics_mv();

-- ========================================
-- View Sizes and Row Counts
-- ========================================

SELECT
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) AS size,
    (SELECT count(*) FROM pg_class WHERE relname = matviewname) as row_count
FROM pg_matviews
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||matviewname) DESC;

-- ========================================
-- Usage Examples
-- ========================================

-- Refresh all views:
-- SELECT refresh_all_analytics_mv();

-- Refresh realtime views only:
-- SELECT refresh_realtime_mv();

-- Query daily sales:
-- SELECT * FROM mv_daily_sales WHERE sale_date >= CURRENT_DATE - 30 ORDER BY sale_date DESC;

-- Top products by revenue:
-- SELECT product_name, total_revenue, total_profit FROM mv_product_performance ORDER BY total_revenue DESC LIMIT 10;

-- Customer RFM analysis:
-- SELECT name, segment, recency_score, frequency_score, monetary_score FROM mv_customer_segments ORDER BY monetary_value DESC LIMIT 20;

-- ========================================
-- Performance Notes
-- ========================================

COMMENT ON MATERIALIZED VIEW mv_daily_sales IS
    'Daily aggregated sales metrics. Refresh every 15-30 minutes for near-realtime dashboard.';

COMMENT ON MATERIALIZED VIEW mv_product_performance IS
    'Product-level performance metrics including revenue, profit, and quantity sold. Refresh daily.';

COMMENT ON MATERIALIZED VIEW mv_customer_segments IS
    'Customer segmentation with RFM analysis. Refresh daily.';

COMMENT ON MATERIALIZED VIEW mv_category_performance IS
    'Category-level performance metrics. Refresh daily.';

COMMENT ON MATERIALIZED VIEW mv_sales_rep_performance IS
    'Sales representative performance metrics. Refresh daily.';

COMMENT ON MATERIALIZED VIEW mv_hourly_metrics IS
    'Hourly metrics for the last 7 days. Refresh every 15 minutes.';

-- Benefits of materialized views:
-- 1. Pre-computed aggregations = faster queries
-- 2. Reduced load on main tables
-- 3. Consistent query performance
-- 4. Can be indexed for even faster access
-- 5. CONCURRENTLY refresh allows queries during refresh
