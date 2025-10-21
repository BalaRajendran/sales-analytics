-- Pre-computed Aggregation Tables for Ultra-Fast Queries
-- These tables store pre-aggregated data for instant dashboard response

-- Hourly Metrics Aggregation
CREATE TABLE IF NOT EXISTS agg_hourly_metrics (
    metric_hour TIMESTAMPTZ PRIMARY KEY,
    revenue NUMERIC(15,2) NOT NULL DEFAULT 0,
    order_count INTEGER NOT NULL DEFAULT 0,
    avg_order_value NUMERIC(10,2),
    unique_customers INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agg_hourly_hour ON agg_hourly_metrics(metric_hour DESC);

-- Category Performance by Period
CREATE TABLE IF NOT EXISTS agg_category_performance (
    id SERIAL PRIMARY KEY,
    category_id UUID NOT NULL REFERENCES categories(id),
    period VARCHAR(20) NOT NULL,  -- 'today', 'week', 'month', 'quarter', 'year'
    revenue NUMERIC(15,2) NOT NULL DEFAULT 0,
    profit NUMERIC(15,2) NOT NULL DEFAULT 0,
    units_sold INTEGER NOT NULL DEFAULT 0,
    order_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category_id, period)
);

CREATE INDEX IF NOT EXISTS idx_agg_cat_perf_category ON agg_category_performance(category_id);
CREATE INDEX IF NOT EXISTS idx_agg_cat_perf_period ON agg_category_performance(period);

COMMENT ON TABLE agg_hourly_metrics IS 'Pre-computed hourly metrics for fast queries';
COMMENT ON TABLE agg_category_performance IS 'Pre-computed category performance by time period';
