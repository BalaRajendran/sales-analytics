-- Partition Orders Table - DISABLED
-- This script is intentionally left empty as partitioning is disabled by default
-- Partitioning will be implemented later when needed for performance optimization

-- To enable partitioning in the future:
-- 1. Update src/models/order.py to uncomment postgresql_partition_by
-- 2. Recreate the orders table with partitioning
-- 3. Add partition creation statements here

\echo 'NOTICE: Order table partitioning is disabled'
\echo 'NOTICE: This is intentional - partitioning will be added later'

-- Empty script - no operations to perform
SELECT 1 as partition_script_skipped;
