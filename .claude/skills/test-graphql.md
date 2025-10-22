# Test GraphQL Query

Test a GraphQL query against the running FastAPI server.

## Instructions

1. First, check if the server is running on http://localhost:8000
2. If not running, ask the user if they want to start it
3. Execute the GraphQL query provided by the user using curl
4. Display the formatted response
5. If there are errors, explain what went wrong and suggest fixes

## Usage

- User provides a GraphQL query
- You execute it against http://localhost:8000/graphql
- Show the results in a formatted way

## Example Query Format

```graphql
query {
  salesOverview(period: MONTH) {
    totalRevenue
    totalOrders
    averageOrderValue
  }
}
```

## Curl Command Template

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "QUERY_HERE"}'
```

## Tips

- Pretty print JSON responses using `jq` if available
- Check for common errors: authentication, malformed queries, server not running
- Suggest query improvements based on the schema
