# GraphQL Query Examples

This document contains all working GraphQL queries for the Sales Dashboard API.

## Table of Contents
- [Dashboard Queries](#dashboard-queries)
- [Product Queries](#product-queries)
- [Customer Queries](#customer-queries)
- [Order Queries](#order-queries)
- [Analytics Queries](#analytics-queries)
- [Cache Queries](#cache-queries)

---

## Dashboard Queries

### 1. Dashboard Overview

Get complete dashboard metrics with revenue, orders, and trends.

```graphql
query GetDashboardOverview($dateRange: DateRangeEnum = LAST_7_DAYS) {
  dashboardOverview(dateRange: $dateRange) {
    revenueMetrics {
      totalRevenue
      totalProfit
      profitMarginPercentage
      revenueGrowth
    }
    orderMetrics {
      totalOrders
      completedOrders
      pendingOrders
      cancelledOrders
      avgOrderValue
    }
    topProducts {
      productId
      productName
      categoryName
      timesSold
      totalRevenue
      totalProfit
      stockQuantity
    }
    topCategories {
      categoryId
      categoryName
      productsCount
      totalRevenue
      totalProfit
      revenueContributionPercentage
    }
    revenueTrend {
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
    dateRange
    startDate
    endDate
  }
}
```

**Variables:**
```json
{
  "dateRange": "LAST_7_DAYS"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "operationName": "GetDashboardOverview",
    "variables": {"dateRange": "LAST_7_DAYS"},
    "query": "query GetDashboardOverview($dateRange: DateRangeEnum = LAST_7_DAYS) { dashboardOverview(dateRange: $dateRange) { revenueMetrics { totalRevenue totalProfit profitMarginPercentage } orderMetrics { totalOrders completedOrders pendingOrders cancelledOrders avgOrderValue } dateRange startDate endDate } }"
  }'
```

---

### 2. Realtime Metrics

Get real-time dashboard metrics for today.

```graphql
query GetRealtimeMetrics {
  realtimeMetrics {
    activeUsers
    pendingOrders
    revenueToday
    ordersToday
    avgOrderValueToday
    timestamp
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { realtimeMetrics { activeUsers pendingOrders revenueToday ordersToday avgOrderValueToday timestamp } }"
  }'
```

---

## Product Queries

### 3. Get All Products (Paginated)

**IMPORTANT:** The `products` query returns a `ProductConnection` type, not a direct array. You must query `edges` and `pageInfo`.

**❌ INCORRECT Query:**
```graphql
query GetAllProducts {
  products {
    id
    name
    sku
    price
  }
}
```

**✅ CORRECT Query:**
```graphql
query GetAllProducts($limit: Int = 20, $offset: Int = 0, $filter: ProductFilter) {
  products(limit: $limit, offset: $offset, filter: $filter) {
    edges {
      id
      name
      categoryId
      costPrice
      sellingPrice
      stockQuantity
      profitMarginPercentage
      createdAt
      updatedAt
      category {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Variables:**
```json
{
  "limit": 20,
  "offset": 0,
  "filter": null
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "operationName": "GetAllProducts",
    "variables": {"limit": 20, "offset": 0},
    "query": "query GetAllProducts($limit: Int, $offset: Int, $filter: ProductFilter) { products(limit: $limit, offset: $offset, filter: $filter) { edges { id name sellingPrice stockQuantity profitMarginPercentage category { name } } pageInfo { hasNextPage hasPreviousPage totalCount } } }"
  }'
```

---

### 4. Get Products with Filters

Filter products by category, price range, stock status, or search term.

```graphql
query GetFilteredProducts(
  $limit: Int = 20
  $offset: Int = 0
  $filter: ProductFilter
) {
  products(limit: $limit, offset: $offset, filter: $filter) {
    edges {
      id
      name
      sellingPrice
      costPrice
      stockQuantity
      profitMargin
      profitMarginPercentage
      category {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Variables:**
```json
{
  "limit": 20,
  "offset": 0,
  "filter": {
    "categoryId": "uuid-here",
    "minPrice": 10.00,
    "maxPrice": 100.00,
    "inStock": true,
    "search": "laptop"
  }
}
```

---

### 5. Get Single Product by ID

```graphql
query GetProduct($productId: UUID!) {
  product(productId: $productId) {
    id
    name
    categoryId
    costPrice
    sellingPrice
    stockQuantity
    profitMargin
    profitMarginPercentage
    createdAt
    updatedAt
    category {
      id
      name
      parentId
    }
  }
}
```

**Variables:**
```json
{
  "productId": "uuid-here"
}
```

---

### 6. Product Performance

Get top performing products by revenue.

```graphql
query GetProductPerformance(
  $dateRange: DateRangeEnum = LAST_30_DAYS
  $limit: Int = 10
) {
  productPerformance(dateRange: $dateRange, limit: $limit) {
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

**Variables:**
```json
{
  "dateRange": "LAST_30_DAYS",
  "limit": 10
}
```

---

## Customer Queries

### 7. Get All Customers (Paginated)

**✅ CORRECT Query:**
```graphql
query GetAllCustomers($limit: Int = 20, $offset: Int = 0, $filter: CustomerFilter) {
  customers(limit: $limit, offset: $offset, filter: $filter) {
    edges {
      id
      name
      email
      segment
      totalLifetimeValue
      createdAt
      updatedAt
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Variables:**
```json
{
  "limit": 20,
  "offset": 0,
  "filter": null
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "operationName": "GetAllCustomers",
    "variables": {"limit": 20, "offset": 0},
    "query": "query GetAllCustomers($limit: Int, $offset: Int) { customers(limit: $limit, offset: $offset) { edges { id name email segment totalLifetimeValue } pageInfo { hasNextPage hasPreviousPage totalCount } } }"
  }'
```

---

### 8. Get Customers with Filters

```graphql
query GetFilteredCustomers(
  $limit: Int = 20
  $offset: Int = 0
  $filter: CustomerFilter
) {
  customers(limit: $limit, offset: $offset, filter: $filter) {
    edges {
      id
      name
      email
      segment
      totalLifetimeValue
      createdAt
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Variables:**
```json
{
  "limit": 20,
  "offset": 0,
  "filter": {
    "segment": "PREMIUM",
    "minLifetimeValue": 1000.00,
    "search": "john"
  }
}
```

---

### 9. Get Single Customer by ID

```graphql
query GetCustomer($customerId: UUID!) {
  customer(customerId: $customerId) {
    id
    name
    email
    segment
    totalLifetimeValue
    createdAt
    updatedAt
  }
}
```

**Variables:**
```json
{
  "customerId": "uuid-here"
}
```

---

### 10. Customer Segment Distribution

```graphql
query GetCustomerSegments {
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

### 11. Get All Orders (Paginated)

**✅ CORRECT Query:**
```graphql
query GetAllOrders($limit: Int = 20, $offset: Int = 0, $filter: OrderFilter) {
  orders(limit: $limit, offset: $offset, filter: $filter) {
    edges {
      id
      customerId
      salesRepId
      orderDate
      totalAmount
      status
      profit
      createdAt
      updatedAt
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Variables:**
```json
{
  "limit": 20,
  "offset": 0,
  "filter": null
}
```

---

### 12. Get Orders with Filters

```graphql
query GetFilteredOrders(
  $limit: Int = 20
  $offset: Int = 0
  $filter: OrderFilter
) {
  orders(limit: $limit, offset: $offset, filter: $filter) {
    edges {
      id
      orderDate
      totalAmount
      status
      profit
      customerId
      salesRepId
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      totalCount
    }
  }
}
```

**Variables:**
```json
{
  "limit": 20,
  "offset": 0,
  "filter": {
    "customerId": "uuid-here",
    "salesRepId": "uuid-here",
    "status": "COMPLETED",
    "dateFrom": "2025-01-01T00:00:00Z",
    "dateTo": "2025-12-31T23:59:59Z",
    "minAmount": 100.00,
    "maxAmount": 1000.00
  }
}
```

---

### 13. Get Single Order by ID

```graphql
query GetOrder($orderId: UUID!) {
  order(orderId: $orderId) {
    id
    customerId
    salesRepId
    orderDate
    totalAmount
    status
    profit
    createdAt
    updatedAt
  }
}
```

**Variables:**
```json
{
  "orderId": "uuid-here"
}
```

---

## Analytics Queries

### 14. Profit Analysis

Get detailed profit metrics for a date range.

```graphql
query GetProfitAnalysis($dateRange: DateRangeEnum = LAST_30_DAYS) {
  profitAnalysis(dateRange: $dateRange) {
    totalRevenue
    totalCost
    totalProfit
    profitMarginPercentage
  }
}
```

**Variables:**
```json
{
  "dateRange": "LAST_30_DAYS"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "operationName": "GetProfitAnalysis",
    "variables": {"dateRange": "LAST_30_DAYS"},
    "query": "query GetProfitAnalysis($dateRange: DateRangeEnum) { profitAnalysis(dateRange: $dateRange) { totalRevenue totalCost totalProfit profitMarginPercentage } }"
  }'
```

---

### 15. Regional Performance

Get sales performance by region.

```graphql
query GetRegionalPerformance($dateRange: DateRangeEnum = LAST_30_DAYS) {
  regionalPerformance(dateRange: $dateRange) {
    region
    totalRevenue
    totalOrders
    salesRepsCount
    avgOrderValue
    revenueContributionPercentage
  }
}
```

**Variables:**
```json
{
  "dateRange": "LAST_30_DAYS"
}
```

---

## Cache Queries

### 16. Cache Info

Get cache performance statistics.

```graphql
query GetCacheInfo {
  cacheInfo {
    cacheHits
    cacheMisses
    hitRatePercentage
    isCached
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { cacheInfo { cacheHits cacheMisses hitRatePercentage isCached } }"
  }'
```

---

## Common Enums

### DateRangeEnum
```
TODAY
YESTERDAY
LAST_7_DAYS
LAST_30_DAYS
LAST_90_DAYS
THIS_MONTH
LAST_MONTH
THIS_YEAR
CUSTOM
```

### OrderStatus
```
PENDING
PROCESSING
COMPLETED
CANCELLED
REFUNDED
```

### CustomerSegment
```
PREMIUM
REGULAR
NEW
AT_RISK
CHURNED
```

---

## Important Notes

### Pagination Pattern

All list queries (`products`, `customers`, `orders`) return a **Connection** type with this structure:

```graphql
{
  edges {
    # Actual data items
  }
  pageInfo {
    hasNextPage
    hasPreviousPage
    totalCount
  }
}
```

**Always query `edges` to access the actual data!**

### Filter Types

**ProductFilter:**
```graphql
{
  categoryId: UUID
  minPrice: Decimal
  maxPrice: Decimal
  inStock: Boolean
  search: String
}
```

**CustomerFilter:**
```graphql
{
  segment: CustomerSegment
  minLifetimeValue: Decimal
  search: String
}
```

**OrderFilter:**
```graphql
{
  customerId: UUID
  salesRepId: UUID
  status: OrderStatus
  dateFrom: DateTime
  dateTo: DateTime
  minAmount: Decimal
  maxAmount: Decimal
}
```

---

## Testing All Queries

Run the automated test script:
```bash
./test_all_queries_auto.sh
```

This will test all 10 major queries and generate a report in `test_results.md`.
