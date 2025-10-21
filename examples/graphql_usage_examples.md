# GraphQL API Usage Examples

Complete examples for using the Sales Dashboard GraphQL API.

## Accessing GraphQL Playground

Once the server is running, access the GraphQL Playground at:
- **GraphQL Endpoint**: `http://localhost:8000/graphql`
- **GraphQL Playground**: `http://localhost:8000/graphql` (in browser)

## Table of Contents

1. [Dashboard Queries](#dashboard-queries)
2. [Product Queries](#product-queries)
3. [Customer Queries](#customer-queries)
4. [Order Queries](#order-queries)
5. [Analytics Queries](#analytics-queries)
6. [Mutations](#mutations)
7. [Advanced Patterns](#advanced-patterns)

---

## Dashboard Queries

### 1. Get Complete Dashboard Overview

```graphql
query DashboardOverview {
  dashboardOverview(dateRange: LAST_7_DAYS) {
    # Revenue Metrics
    revenueMetrics {
      totalRevenue
      totalProfit
      profitMarginPercentage
      revenueGrowth
    }

    # Order Metrics
    orderMetrics {
      totalOrders
      completedOrders
      pendingOrders
      cancelledOrders
      avgOrderValue
      ordersGrowth
    }

    # Top Products
    topProducts {
      productId
      productName
      categoryName
      timesSold
      totalRevenue
      totalProfit
      profitMarginPercentage
      stockQuantity
      revenueRank
    }

    # Top Categories
    topCategories {
      categoryId
      categoryName
      productsCount
      totalRevenue
      totalProfit
      revenueContributionPercentage
    }

    # Top Customers
    topCustomers {
      customerId
      customerName
      customerEmail
      segment
      totalOrders
      totalRevenue
      avgOrderValue
      lifetimeValue
    }

    # Top Sales Reps
    topSalesReps {
      salesRepId
      salesRepName
      region
      totalSales
      totalOrders
      avgOrderValue
      commissionEarned
      revenueContributionPercentage
    }

    # Revenue Trend
    revenueTrend {
      period
      dataPoints {
        date
        value
        label
      }
      total
      average
      growthRate
      trendDirection
    }

    # Order Trend
    orderTrend {
      period
      dataPoints {
        date
        value
        label
      }
      total
      average
      trendDirection
    }

    # Metadata
    dateRange
    startDate
    endDate
    cachedAt
  }
}
```

### 2. Get Real-Time Metrics

```graphql
query RealtimeMetrics {
  realtimeMetrics {
    activeUsers
    pendingOrders
    revenueToday
    ordersToday
    avgOrderValueToday
    topSellingProductToday
    timestamp
  }
}
```

### 3. Custom Date Range Dashboard

```graphql
query CustomDateRangeDashboard {
  dashboardOverview(
    dateRange: CUSTOM
    customRange: {
      startDate: "2024-01-01T00:00:00Z"
      endDate: "2024-12-31T23:59:59Z"
    }
  ) {
    revenueMetrics {
      totalRevenue
      totalProfit
    }
    orderMetrics {
      totalOrders
      avgOrderValue
    }
    startDate
    endDate
  }
}
```

---

## Product Queries

### 4. Get Single Product

```graphql
query GetProduct($productId: UUID!) {
  product(productId: $productId) {
    id
    name
    costPrice
    sellingPrice
    stockQuantity
    profitMargin
    profitMarginPercentage
    category {
      id
      name
    }
    createdAt
    updatedAt
  }
}

# Variables
{
  "productId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 5. Get Paginated Products with Filters

```graphql
query GetProducts(
  $filter: ProductFilter
  $limit: Int = 20
  $offset: Int = 0
) {
  products(filter: $filter, limit: $limit, offset: $offset) {
    edges {
      id
      name
      sellingPrice
      stockQuantity
      profitMarginPercentage
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}

# Variables
{
  "filter": {
    "categoryId": "550e8400-e29b-41d4-a716-446655440001",
    "minPrice": 10.00,
    "maxPrice": 100.00,
    "inStock": true,
    "search": "laptop"
  },
  "limit": 10,
  "offset": 0
}
```

### 6. Get Product Performance

```graphql
query ProductPerformance {
  productPerformance(dateRange: LAST_30_DAYS, limit: 10) {
    productId
    productName
    categoryName
    timesSold
    totalRevenue
    totalProfit
    profitMarginPercentage
    stockQuantity
    revenueRank
  }
}
```

---

## Customer Queries

### 7. Get Single Customer

```graphql
query GetCustomer($customerId: UUID!) {
  customer(customerId: $customerId) {
    id
    name
    email
    segment
    totalLifetimeValue
    ordersCount
    avgOrderValue
    createdAt
    updatedAt
  }
}

# Variables
{
  "customerId": "550e8400-e29b-41d4-a716-446655440002"
}
```

### 8. Get Customers with Filters

```graphql
query GetCustomers($filter: CustomerFilter) {
  customers(filter: $filter, limit: 20, offset: 0) {
    edges {
      id
      name
      email
      segment
      totalLifetimeValue
      ordersCount
    }
    pageInfo {
      hasNextPage
      totalCount
    }
  }
}

# Variables
{
  "filter": {
    "segment": "PREMIUM",
    "minLifetimeValue": 5000.00,
    "search": "john"
  }
}
```

### 9. Get Customer Segment Distribution

```graphql
query CustomerSegments {
  customerSegmentDistribution {
    segment
    customerCount
    totalRevenue
    avgLifetimeValue
    percentage
  }
}
```

---

## Order Queries

### 10. Get Single Order

```graphql
query GetOrder($orderId: UUID!) {
  order(orderId: $orderId) {
    id
    orderDate
    totalAmount
    status
    profit
    customer {
      id
      name
      email
    }
    salesRep {
      id
      name
      region
    }
    items {
      id
      quantity
      unitPrice
      totalPrice
      profit
      product {
        id
        name
      }
    }
    createdAt
  }
}

# Variables
{
  "orderId": "550e8400-e29b-41d4-a716-446655440003"
}
```

### 11. Get Orders with Filters

```graphql
query GetOrders($filter: OrderFilter) {
  orders(filter: $filter, limit: 20, offset: 0) {
    edges {
      id
      orderDate
      totalAmount
      status
      profit
      customer {
        name
        email
      }
    }
    pageInfo {
      hasNextPage
      totalCount
    }
  }
}

# Variables
{
  "filter": {
    "status": "COMPLETED",
    "dateFrom": "2024-01-01T00:00:00Z",
    "dateTo": "2024-12-31T23:59:59Z",
    "minAmount": 100.00
  }
}
```

---

## Analytics Queries

### 12. Get Profit Analysis

```graphql
query ProfitAnalysis {
  profitAnalysis(dateRange: LAST_30_DAYS) {
    totalRevenue
    totalCost
    totalProfit
    profitMarginPercentage
    bestProfitMarginProduct {
      productName
      profitMarginPercentage
    }
    bestProfitMarginCategory {
      categoryName
      profitMarginPercentage
    }
  }
}
```

### 13. Get Regional Performance

```graphql
query RegionalPerformance {
  regionalPerformance(dateRange: LAST_30_DAYS) {
    region
    totalRevenue
    totalOrders
    salesRepsCount
    avgOrderValue
    revenueContributionPercentage
  }
}
```

### 14. Get Cache Information

```graphql
query CacheInfo {
  cacheInfo {
    cacheHits
    cacheMisses
    hitRatePercentage
    isCached
  }
}
```

---

## Mutations

### 15. Create Product

```graphql
mutation CreateProduct($input: CreateProductInput!) {
  createProduct(input: $input) {
    success
    message
    errors
    product {
      id
      name
      sellingPrice
      stockQuantity
    }
  }
}

# Variables
{
  "input": {
    "name": "MacBook Pro 16-inch",
    "categoryId": "550e8400-e29b-41d4-a716-446655440001",
    "costPrice": 1800.00,
    "sellingPrice": 2499.99,
    "stockQuantity": 50
  }
}
```

### 16. Update Product

```graphql
mutation UpdateProduct(
  $productId: UUID!
  $input: UpdateProductInput!
) {
  updateProduct(productId: $productId, input: $input) {
    success
    message
    errors
    product {
      id
      name
      sellingPrice
      stockQuantity
      profitMarginPercentage
    }
  }
}

# Variables
{
  "productId": "550e8400-e29b-41d4-a716-446655440000",
  "input": {
    "sellingPrice": 2599.99,
    "stockQuantity": 45
  }
}
```

### 17. Delete Product

```graphql
mutation DeleteProduct($productId: UUID!) {
  deleteProduct(productId: $productId) {
    success
    message
    errors
  }
}

# Variables
{
  "productId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 18. Create Customer

```graphql
mutation CreateCustomer($input: CreateCustomerInput!) {
  createCustomer(input: $input) {
    success
    message
    errors
    customer {
      id
      name
      email
      segment
    }
  }
}

# Variables
{
  "input": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "segment": "REGULAR"
  }
}
```

### 19. Update Customer

```graphql
mutation UpdateCustomer(
  $customerId: UUID!
  $input: UpdateCustomerInput!
) {
  updateCustomer(customerId: $customerId, input: $input) {
    success
    message
    errors
    customer {
      id
      name
      segment
      totalLifetimeValue
    }
  }
}

# Variables
{
  "customerId": "550e8400-e29b-41d4-a716-446655440002",
  "input": {
    "segment": "PREMIUM",
    "totalLifetimeValue": 15000.00
  }
}
```

### 20. Create Order

```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    success
    message
    errors
    order {
      id
      orderDate
      totalAmount
      status
    }
  }
}

# Variables
{
  "input": {
    "customerId": "550e8400-e29b-41d4-a716-446655440002",
    "salesRepId": "550e8400-e29b-41d4-a716-446655440004",
    "orderDate": "2024-10-20T10:30:00Z",
    "items": [
      {
        "productId": "550e8400-e29b-41d4-a716-446655440000",
        "quantity": 2,
        "unitPrice": 2499.99
      },
      {
        "productId": "550e8400-e29b-41d4-a716-446655440005",
        "quantity": 1,
        "unitPrice": 199.99
      }
    ]
  }
}
```

### 21. Update Order Status

```graphql
mutation UpdateOrderStatus($input: UpdateOrderStatusInput!) {
  updateOrderStatus(input: $input) {
    success
    message
    errors
    order {
      id
      status
      totalAmount
    }
  }
}

# Variables
{
  "input": {
    "orderId": "550e8400-e29b-41d4-a716-446655440003",
    "status": "COMPLETED"
  }
}
```

### 22. Cancel Order

```graphql
mutation CancelOrder($orderId: UUID!) {
  cancelOrder(orderId: $orderId) {
    success
    message
    errors
    order {
      id
      status
    }
  }
}

# Variables
{
  "orderId": "550e8400-e29b-41d4-a716-446655440003"
}
```

### 23. Clear Cache

```graphql
mutation ClearCache($pattern: String) {
  clearCache(cachePattern: $pattern) {
    success
    message
    errors
  }
}

# Clear all product caches
{
  "pattern": "product:*"
}

# Clear all caches (use with caution!)
{
  "pattern": null
}
```

---

## Advanced Patterns

### 24. Complex Dashboard Query with Fragments

```graphql
fragment MetricsFragment on RevenueMetrics {
  totalRevenue
  totalProfit
  profitMarginPercentage
}

fragment ProductFragment on ProductPerformance {
  productName
  totalRevenue
  totalProfit
  profitMarginPercentage
}

query AdvancedDashboard {
  dashboardOverview(dateRange: LAST_30_DAYS) {
    revenueMetrics {
      ...MetricsFragment
    }
    topProducts {
      ...ProductFragment
      timesSold
      stockQuantity
    }
    revenueTrend {
      dataPoints {
        date
        value
      }
      trendDirection
    }
  }
}
```

### 25. Multiple Queries in One Request

```graphql
query MultiQuery {
  # Get dashboard
  dashboard: dashboardOverview(dateRange: LAST_7_DAYS) {
    revenueMetrics {
      totalRevenue
    }
  }

  # Get realtime metrics
  realtime: realtimeMetrics {
    revenueToday
    ordersToday
  }

  # Get top products
  products: productPerformance(limit: 5) {
    productName
    totalRevenue
  }

  # Get cache info
  cache: cacheInfo {
    hitRatePercentage
  }
}
```

### 26. Pagination Pattern

```graphql
query PaginatedProducts($offset: Int!, $limit: Int!) {
  products(offset: $offset, limit: $limit) {
    edges {
      id
      name
      sellingPrice
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}

# First page
{ "offset": 0, "limit": 20 }

# Second page
{ "offset": 20, "limit": 20 }

# Third page
{ "offset": 40, "limit": 20 }
```

### 27. Error Handling Pattern

```graphql
mutation CreateProductWithErrorHandling($input: CreateProductInput!) {
  createProduct(input: $input) {
    success
    message
    errors
    product {
      id
      name
    }
  }
}

# Check the response
{
  "data": {
    "createProduct": {
      "success": false,
      "message": "Failed to create product",
      "errors": ["Category with given ID does not exist"],
      "product": null
    }
  }
}
```

---

## Performance Tips

1. **Use Field Selection**: Only request fields you need to reduce payload size
2. **Use DataLoaders**: Automatically batches requests to avoid N+1 queries
3. **Leverage Caching**: Most analytics queries are cached with appropriate TTL
4. **Use Pagination**: For large lists, always use pagination
5. **Check Cache Stats**: Monitor `cacheInfo` query to ensure good hit rates

## Authentication (To Be Implemented)

When authentication is added, include the JWT token in headers:

```http
POST /graphql
Content-Type: application/json
Authorization: Bearer <your-jwt-token>

{
  "query": "query { dashboardOverview { ... } }"
}
```

## Rate Limiting

The API has rate limiting enabled:
- Default: 1000 requests per minute per IP
- GraphQL counts as 1 request regardless of query complexity
- Check response headers for rate limit info

---

## Testing with cURL

```bash
# Simple query
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ realtimeMetrics { revenueToday ordersToday } }"}'

# Query with variables
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetProduct($id: UUID!) { product(productId: $id) { name sellingPrice } }",
    "variables": {"id": "550e8400-e29b-41d4-a716-446655440000"}
  }'
```

---

## Next Steps

- Implement subscriptions for real-time updates
- Add authentication and authorization
- Add query complexity limits
- Add persisted queries for production
- Monitor query performance with APM tools
