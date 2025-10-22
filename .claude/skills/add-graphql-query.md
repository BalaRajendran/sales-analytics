# Add New GraphQL Query

Guide to adding a new GraphQL query to the application following project conventions.

## Instructions

1. Understand what data the query needs to fetch
2. Create/update necessary service methods
3. Add GraphQL type definitions
4. Create the query resolver
5. Update the schema
6. Write tests for the new query
7. Update documentation

## Step-by-Step Process

### 1. Define the Service Method

Location: `src/services/`

Example:
```python
# src/services/analytics_service.py
async def get_revenue_by_region(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime
) -> List[Dict]:
    # Implementation
    pass
```

### 2. Add GraphQL Types

Location: `src/graphql/types.py`

Example:
```python
@strawberry.type
class RevenueByRegion:
    region: str
    total_revenue: Decimal
    order_count: int
    average_order_value: Decimal
```

### 3. Create Query Resolver

Location: `src/graphql/queries.py`

Example:
```python
@strawberry.type
class Query:
    @strawberry.field
    async def revenue_by_region(
        self,
        info: Info,
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueByRegion]:
        db = info.context["db"]
        data = await analytics_service.get_revenue_by_region(
            db, start_date, end_date
        )
        return [RevenueByRegion(**item) for item in data]
```

### 4. Add Caching (if applicable)

Use the cache decorator:
```python
from src.core.cache_decorators import cached

@cached(ttl=300, key_prefix="revenue_by_region")
async def get_revenue_by_region(...):
    # Implementation
```

### 5. Write Tests

Location: `tests/integration/`

Example:
```python
# tests/integration/test_revenue_queries.py
async def test_revenue_by_region(graphql_client):
    query = """
        query {
            revenueByRegion(
                startDate: "2024-01-01T00:00:00",
                endDate: "2024-12-31T23:59:59"
            ) {
                region
                totalRevenue
                orderCount
            }
        }
    """
    response = await graphql_client.execute(query)
    assert response.get("errors") is None
    assert len(response["data"]["revenueByRegion"]) > 0
```

### 6. Update Documentation

Add the query example to:
- `docs/GRAPHQL_QUERY_EXAMPLES.md`
- Update `docs/API.md` if needed

## Best Practices

1. **Use DataLoaders** for N+1 query prevention
2. **Add caching** for expensive queries
3. **Add field-level permissions** if needed
4. **Validate inputs** using Strawberry's built-in validators
5. **Handle errors gracefully** with proper error messages
6. **Add query complexity** limits if needed
7. **Document the query** with docstrings

## Query Complexity

For expensive queries, add complexity estimation:
```python
@strawberry.field(
    extensions=[
        ComplexityExtension(complexity=10)
    ]
)
async def expensive_query(...):
    pass
```

## Testing Checklist

- [ ] Unit test for service method
- [ ] Integration test for GraphQL query
- [ ] Test with various inputs
- [ ] Test error cases
- [ ] Test caching behavior
- [ ] Test performance with large datasets
- [ ] Update query examples documentation

## Example Complete Flow

User wants to add: "Get top customers by purchase frequency"

1. Create service method in `src/services/customer_service.py`
2. Define `TopCustomer` type in `src/graphql/types.py`
3. Add `topCustomersByFrequency` query in `src/graphql/queries.py`
4. Add caching with 5-minute TTL
5. Write tests in `tests/integration/test_customer_queries.py`
6. Add example to documentation
