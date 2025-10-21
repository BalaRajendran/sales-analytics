# Database Migrations Guide

Complete guide for managing database migrations in the ShopX Sales Analytics project.

## Table of Contents

- [Quick Start](#quick-start)
- [Migration Commands](#migration-commands)
- [Migration Workflow](#migration-workflow)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Quick Start

### Initial Setup

```bash
# 1. Start database services
make dev-up

# 2. Run all migrations (Alembic + SQL optimizations)
make migrate-all

# 3. (Optional) Seed with sample data
make db-seed
```

That's it! Your database is now ready.

## Migration Commands

### Run Migrations

```bash
# Run Alembic migrations only (schema)
make migrate

# Apply SQL optimization scripts only
make migrate-sql

# Run ALL migrations (recommended)
make migrate-all
```

### Manage Migrations

```bash
# Create new migration
make migrate-create
# Prompts: "Enter migration message: add user table"

# Check current migration
make migrate-current

# View migration history
make migrate-history

# Rollback one migration
make migrate-down
```

### Database Operations

```bash
# Open database shell
make db-shell

# Reset database (DANGER: deletes all data)
make db-reset

# Seed database with sample data
make db-seed

# Backup database
make db-backup

# Restore from backup
make db-restore
```

## Migration Workflow

### Two-Phase Migration System

This project uses a **two-phase migration system**:

#### Phase 1: Schema Migrations (Alembic)

Handles table structure and relationships:
- Creating tables
- Adding/removing columns
- Modifying constraints
- Foreign key relationships

**Location**: Auto-generated Python files in `migrations/versions/*.py`

#### Phase 2: Optimizations (SQL Scripts)

Handles performance optimizations:
- Indexes for query performance
- Table partitioning for scalability
- Materialized views for analytics
- Aggregation tables for reporting

**Location**: Manual SQL scripts in `migrations/versions/*.sql`

### Migration Order

**IMPORTANT**: Always run migrations in this order:

```bash
1. make migrate      # Alembic first (creates schema)
2. make migrate-sql  # SQL scripts second (optimizes schema)
```

Or use the combined command:

```bash
make migrate-all  # Runs both in correct order
```

## SQL Optimization Scripts

### 001_create_indexes.sql

Creates indexes for frequently queried columns:

```sql
-- Example indexes
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_products_category_id ON products(category_id);
```

**Purpose**: Speeds up queries by 10-100x on large datasets

### 002_partition_orders.sql

Partitions the orders table by month:

```sql
-- Creates monthly partitions for orders
-- Automatically routes data to correct partition
```

**Purpose**: Improves query performance on large order history

**Benefits**:
- Faster queries on date ranges
- Easier data archival
- Better maintenance operations

### 003_materialized_views.sql

Creates pre-computed views for analytics:

```sql
-- Examples:
-- - daily_sales_summary
-- - product_performance
-- - customer_lifetime_value
```

**Purpose**: Sub-second response times for complex analytics

**Refresh Strategy**:
- Auto-refreshed by Celery tasks every 30-60 seconds
- Manual refresh: `REFRESH MATERIALIZED VIEW view_name;`

### 004_aggregation_tables.sql

Creates pre-aggregated data tables:

```sql
-- Hourly, daily, monthly aggregations
-- Reduces real-time computation load
```

**Purpose**: Lightning-fast dashboard metrics

## Configuration

### Environment Variables

Set in your `.env` file:

```env
# Database connection
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Pool settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

### Alembic Configuration

See [alembic.ini](../alembic.ini) and [migrations/env.py](../migrations/env.py)

**Key features**:
- Auto-loads `DATABASE_URL` from settings
- Async-compatible (uses asyncpg)
- Auto-discovers all models

## Troubleshooting

### Common Issues

#### 1. "DATABASE_URL not set"

```bash
# Error when running make migrate-sql
✗ ERROR: DATABASE_URL not set in environment

# Solution: Check your .env file
cp .env.example .env
# Edit .env and set DATABASE_URL
```

#### 2. "relation already exists"

```bash
# Error: Table or index already exists

# Solution 1: Skip migration if already applied
# (migrations are idempotent by design)

# Solution 2: Reset database
make db-reset
make migrate-all
```

#### 3. "database does not exist"

```bash
# Error: Connection failed

# Solution: Start database first
make dev-up

# Wait a few seconds for database to be ready
sleep 5

# Then run migrations
make migrate-all
```

#### 4. "permission denied"

```bash
# Error: Cannot create indexes/partitions

# Solution: Check database user permissions
psql $DATABASE_URL -c "\du"

# Ensure user has CREATE, ALTER permissions
```

#### 5. Migration conflict

```bash
# Error: Multiple heads detected

# Solution: Merge migrations
alembic merge heads -m "merge migrations"
```

### Debug Mode

Enable query logging to debug migration issues:

```env
# In .env file
ENABLE_QUERY_LOGGING=true
GRAPHQL_DEBUG=true
```

### Manual Migration

If Make commands fail, run manually:

```bash
# Load environment
source .venv/bin/activate
export $(cat .env | xargs)

# Run Alembic
alembic upgrade head

# Run SQL scripts
psql $DATABASE_URL -f migrations/versions/001_create_indexes.sql
psql $DATABASE_URL -f migrations/versions/002_partition_orders.sql
psql $DATABASE_URL -f migrations/versions/003_materialized_views.sql
psql $DATABASE_URL -f migrations/versions/004_aggregation_tables.sql
```

## Best Practices

### 1. Always Test Migrations

```bash
# Test on a copy of production data
make db-backup
make migrate-all

# If issues occur
make db-restore
```

### 2. Review Auto-Generated Migrations

```bash
# After creating migration
make migrate-create

# Review the generated file
cat migrations/versions/xxxxx_your_migration.py

# Edit if needed before running
```

### 3. Keep Migrations Small

```bash
# Bad: One migration with 50 changes
make migrate-create  # "add everything"

# Good: Multiple focused migrations
make migrate-create  # "add user table"
make migrate-create  # "add indexes to user table"
make migrate-create  # "add user_profile relationship"
```

### 4. Never Edit Applied Migrations

```bash
# ✗ Bad: Edit old migration file
# ✓ Good: Create new migration to fix issues
make migrate-create  # "fix user table constraint"
```

### 5. Document Complex Migrations

```python
"""Add partitioning to orders table.

Revision ID: abc123
Revises: xyz789
Create Date: 2025-01-20

This migration:
1. Creates monthly partitions for orders table
2. Adds partition maintenance function
3. Sets up automatic partition creation
"""
```

### 6. Backup Before Production Migrations

```bash
# Always backup before running migrations in production
make db-backup

# Run migration
make migrate-all

# Verify
make migrate-current

# If issues, restore
make db-restore
```

### 7. Use Transactions

Alembic migrations should be transactional:

```python
def upgrade() -> None:
    # All operations in one transaction
    op.create_table(...)
    op.create_index(...)
    # If any fails, all roll back
```

### 8. Test Rollback

```bash
# Test that downgrade works
make migrate
make migrate-down

# Then upgrade again
make migrate
```

## Migration Checklist

Before running migrations in production:

- [ ] Backup database (`make db-backup`)
- [ ] Review migration files
- [ ] Test on staging environment
- [ ] Test rollback procedure
- [ ] Document any manual steps
- [ ] Notify team of maintenance window
- [ ] Monitor performance after migration
- [ ] Verify data integrity

## Docker Migrations

### Development Environment

```bash
# Start services
make dev-up

# Run migrations in backend container
docker-compose exec backend uv run alembic upgrade head
```

### Production Environment

```bash
# Run migrations before starting app
docker-compose -f docker-compose.prod.yml run backend alembic upgrade head

# Then start services
make prod-up
```

## Advanced Topics

### Creating Initial Migration

```bash
# Generate initial migration from models
alembic revision --autogenerate -m "initial migration"

# Review and edit the generated file
# Then run
make migrate
```

### Branching Migrations

```bash
# Create branch point
alembic revision -m "branch point"

# Create feature branch
alembic revision --head=abc123 -m "feature branch"

# Merge branches
alembic merge heads -m "merge feature"
```

### Custom Migration Scripts

Create custom SQL scripts for special operations:

```bash
# migrations/versions/005_custom_operation.sql
-- Your custom SQL here
BEGIN;

-- Complex operation that Alembic can't handle
UPDATE orders SET status = 'processed' WHERE status = 'pending';

COMMIT;
```

Run manually:
```bash
psql $DATABASE_URL -f migrations/versions/005_custom_operation.sql
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [Materialized Views](https://www.postgresql.org/docs/current/rules-materializedviews.html)

## Getting Help

```bash
# Show all available commands
make help

# Show migration history
make migrate-history

# Check current state
make migrate-current

# Open database shell for manual inspection
make db-shell
```

---

**Questions?** Check the [main documentation](README.md) or [architecture guide](ARCHITECTURE.md).
