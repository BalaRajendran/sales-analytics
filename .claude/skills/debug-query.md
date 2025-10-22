# Debug Slow GraphQL Query

Analyze and optimize slow-performing GraphQL queries.

## Instructions

1. Identify the slow query
2. Enable query logging and profiling
3. Analyze database query execution
4. Check cache hit rates
5. Identify bottlenecks
6. Suggest optimizations
7. Verify improvements

## Debugging Steps

### 1. Enable SQL Query Logging

Temporarily enable in `src/core/database.py`:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Enable SQL logging
    pool_pre_ping=True,
)
```

### 2. Check Query Execution Plan

```sql
EXPLAIN ANALYZE
SELECT ...;
```

### 3. Monitor Cache Performance

Check Redis stats:
```bash
redis-cli info stats
```

Check cache hit/miss in application logs.

### 4. Profile the Query

Add timing to resolver:
```python
import time

@strawberry.field
async def slow_query(self, info: Info):
    start = time.time()
    result = await service_method()
    duration = time.time() - start
    logger.info(f"Query took {duration:.3f}s")
    return result
```

### 5. Check N+1 Problems

Look for multiple similar queries in logs. Solution: Use DataLoaders.

Example:
```python
# Before (N+1 problem)
for product in products:
    product.category = await get_category(product.category_id)

# After (with DataLoader)
category_loader = info.context["category_loader"]
for product in products:
    product.category = await category_loader.load(product.category_id)
```

### 6. Analyze Database Indexes

```sql
-- Check missing indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

## Common Performance Issues

### 1. Missing Cache

Add caching:
```python
from src.core.cache_decorators import cached

@cached(ttl=300, key_prefix="query_name")
async def get_data():
    # Expensive operation
```

### 2. Missing Index

Add index in migration:
```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_date
ON orders(customer_id, order_date DESC);
```

### 3. Unnecessary Joins

Review query to fetch only needed relationships.

### 4. Large Result Sets

Implement pagination:
```python
@strawberry.field
async def products(
    self,
    info: Info,
    limit: int = 10,
    offset: int = 0
) -> List[Product]:
    # Implement pagination
```

### 5. Complex Aggregations

Consider materialized views:
```sql
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT
    date_trunc('day', order_date) as date,
    SUM(total_amount) as revenue,
    COUNT(*) as order_count
FROM orders
GROUP BY date_trunc('day', order_date);

CREATE INDEX ON daily_sales_summary(date);
```

## Performance Checklist

- [ ] Check query execution time in logs
- [ ] Analyze SQL EXPLAIN ANALYZE output
- [ ] Verify indexes exist for filtered/joined columns
- [ ] Check cache hit rate
- [ ] Look for N+1 query patterns
- [ ] Consider pagination for large results
- [ ] Review relationship loading (eager vs lazy)
- [ ] Check if materialized views would help
- [ ] Verify database connection pool settings
- [ ] Test with production-like data volume

## Optimization Strategies

1. **Add Caching**: Start with 5-minute TTL, adjust based on data freshness needs
2. **Add Indexes**: Create indexes on frequently filtered/sorted columns
3. **Use DataLoaders**: Batch related queries
4. **Add Pagination**: Limit result set size
5. **Materialize Views**: Pre-compute expensive aggregations
6. **Optimize Query**: Reduce joins, select only needed columns
7. **Add Query Complexity Limits**: Prevent overly complex queries

## Verification

After optimization:
1. Run the query multiple times
2. Check execution time improvement
3. Monitor cache hit rate
4. Verify query plan uses indexes
5. Check application logs for reduced query count

## Tools

- PostgreSQL `EXPLAIN ANALYZE`
- Redis `INFO` command
- Application logs with timing
- Prometheus metrics (if configured)
- `pg_stat_statements` extension
