# GraphQL API Documentation

## Overview

The ShopX Analytics API uses GraphQL for flexible, efficient data querying. This document provides complete schema definitions, example queries, and usage patterns.

## Base URL

```
Development: http://localhost:8000/graphql
Production: https://api.shopx.com/graphql
```

## Authentication

All requests require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

---

## Complete Schema

### Scalar Types

```graphql
scalar DateTime
scalar Decimal
scalar UUID
```

### Enums

```graphql
enum Period {
  TODAY
  YESTERDAY
  WEEK
  LAST_WEEK
  MONTH
  LAST_MONTH
  QUARTER
  YEAR
  CUSTOM
}

enum Metric {
  REVENUE
  ORDERS
  CUSTOMERS
  AOV  # Average Order Value
  PROFIT
  MARGIN
}

enum ProductSort {
  REVENUE_DESC
  REVENUE_ASC
  PROFIT_DESC
  PROFIT_ASC
  UNITS_DESC
  UNITS_ASC
  NAME_ASC
  NAME_DESC
}

enum CustomerSegment {
  PREMIUM
  REGULAR
  NEW
  AT_RISK
  CHURNED
}

enum GroupBy {
  PRODUCT
  CATEGORY
  CUSTOMER_SEGMENT
  SALES_REP
  REGION
  DAY
  WEEK
  MONTH
}

enum OrderStatus {
  PENDING
  PROCESSING
  COMPLETED
  CANCELLED
  REFUNDED
}
```

### Input Types

```graphql
input DateRangeInput {
  startDate: DateTime!
  endDate: DateTime!
}

input PaginationInput {
  page: Int = 1
  pageSize: Int = 20
}

input ProductFilterInput {
  categoryId: UUID
  minPrice: Decimal
  maxPrice: Decimal
  inStock: Boolean
}

input CustomerFilterInput {
  segment: CustomerSegment
  minLifetimeValue: Decimal
  maxLifetimeValue: Decimal
}

input OrderFilterInput {
  status: OrderStatus
  customerId: UUID
  salesRepId: UUID
  minAmount: Decimal
  maxAmount: Decimal
}
```

### Object Types

```graphql
# Core Business Types

type Customer {
  id: UUID!
  name: String!
  email: String!
  segment: CustomerSegment
  totalLifetimeValue: Decimal
  createdAt: DateTime!
  updatedAt: DateTime!

  # Analytics
  orders(pagination: PaginationInput): OrderConnection!
  metrics(period: Period!): CustomerMetrics!
}

type Category {
  id: UUID!
  name: String!
  parent: Category
  children: [Category!]!
  createdAt: DateTime!

  # Analytics
  products(pagination: PaginationInput): [Product!]!
  performance(period: Period!): CategoryPerformance!
}

type Product {
  id: UUID!
  name: String!
  category: Category!
  costPrice: Decimal!
  sellingPrice: Decimal!
  stockQuantity: Int!
  createdAt: DateTime!
  updatedAt: DateTime!

  # Computed fields
  profitMargin: Float!
  profitMarginPercentage: Float!

  # Analytics
  performance(period: Period!): ProductPerformance!
  trends(period: Period!, metric: Metric!): [TrendPoint!]!
}

type SalesRepresentative {
  id: UUID!
  name: String!
  email: String!
  region: String
  commissionRate: Decimal
  createdAt: DateTime!

  # Analytics
  performance(period: Period!): SalesRepPerformance!
  orders(pagination: PaginationInput): OrderConnection!
}

type Order {
  id: UUID!
  customer: Customer!
  salesRep: SalesRepresentative
  orderDate: DateTime!
  totalAmount: Decimal!
  status: OrderStatus!
  createdAt: DateTime!

  # Relations
  items: [OrderItem!]!

  # Computed
  itemCount: Int!
  profit: Decimal!
}

type OrderItem {
  id: UUID!
  order: Order!
  product: Product!
  quantity: Int!
  unitPrice: Decimal!
  totalPrice: Decimal!
  createdAt: DateTime!

  # Computed
  profit: Decimal!
}

# Analytics Types

type SalesOverview {
  totalRevenue: Decimal!
  totalOrders: Int!
  averageOrderValue: Decimal!
  uniqueCustomers: Int!

  # Comparisons (vs previous period)
  revenueChange: Float!
  revenueChangePercentage: Float!
  ordersChange: Int!
  ordersChangePercentage: Float!
  aovChange: Decimal!
  aovChangePercentage: Float!
  customersChange: Int!
  customersChangePercentage: Float!

  # Additional metrics
  totalProfit: Decimal
  profitMargin: Float
  conversionRate: Float
  cancelledOrders: Int
  cancelledRevenue: Decimal
}

type TrendPoint {
  timestamp: DateTime!
  value: Decimal!
  label: String!
  change: Float  # % change from previous point
  metadata: TrendMetadata
}

type TrendMetadata {
  orderCount: Int
  customerCount: Int
  averageOrderValue: Decimal
}

type ProductInsight {
  product: Product!
  revenue: Decimal!
  unitsSold: Int!
  profit: Decimal!
  profitMargin: Float!
  growthRate: Float!
  rank: Int!
}

type ProductPerformance {
  product: Product!
  period: Period!

  # Sales metrics
  revenue: Decimal!
  unitsSold: Int!
  orderCount: Int!
  averagePrice: Decimal!

  # Profitability
  profit: Decimal!
  profitMargin: Float!
  profitMarginPercentage: Float!

  # Trends
  growthRate: Float!
  revenueChange: Decimal!
  unitsChange: Int!

  # Dates
  firstSaleDate: DateTime
  lastSaleDate: DateTime
}

type CategoryInsight {
  category: Category!
  revenue: Decimal!
  profit: Decimal!
  profitMargin: Float!
  productCount: Int!
  unitsSold: Int!
  orderCount: Int!
  percentage: Float!  # % of total revenue
}

type CategoryPerformance {
  category: Category!
  period: Period!
  revenue: Decimal!
  profit: Decimal!
  unitsSold: Int!
  productCount: Int!
  topProducts: [ProductInsight!]!
}

type CustomerMetrics {
  customer: Customer!
  period: Period!

  # Order metrics
  orderCount: Int!
  totalSpent: Decimal!
  averageOrderValue: Decimal!

  # Behavior
  lastOrderDate: DateTime
  daysSinceLastOrder: Int
  averageDaysBetweenOrders: Float
  lifetimeDays: Int

  # RFM scores
  recencyScore: Int!  # 1-5 (5 = most recent)
  frequencyScore: Int!  # 1-5 (5 = most frequent)
  monetaryScore: Int!  # 1-5 (5 = highest value)
  rfmScore: String!  # e.g., "555" = best customer
}

type CustomerSegmentSummary {
  segment: CustomerSegment!
  customerCount: Int!
  totalRevenue: Decimal!
  averageLifetimeValue: Decimal!
  averageOrderValue: Decimal!
  percentage: Float!  # % of total customers
}

type CustomerRetentionMetrics {
  period: Period!
  newCustomers: Int!
  returningCustomers: Int!
  churnedCustomers: Int!
  retentionRate: Float!
  churnRate: Float!
  repeatPurchaseRate: Float!
}

type ProfitabilityMetrics {
  period: Period!
  totalRevenue: Decimal!
  totalCost: Decimal!
  totalProfit: Decimal!
  profitMargin: Float!
  averageOrderProfit: Decimal!

  # By segment
  byCategory: [CategoryProfitability!]!
  byProduct: [ProductProfitability!]!
  byCustomerSegment: [SegmentProfitability!]!
}

type CategoryProfitability {
  category: Category!
  revenue: Decimal!
  cost: Decimal!
  profit: Decimal!
  margin: Float!
}

type ProductProfitability {
  product: Product!
  revenue: Decimal!
  cost: Decimal!
  profit: Decimal!
  margin: Float!
  unitsSold: Int!
}

type SegmentProfitability {
  segment: CustomerSegment!
  revenue: Decimal!
  profit: Decimal!
  margin: Float!
  customerCount: Int!
}

type MarginAnalysis {
  groupName: String!
  groupId: UUID
  revenue: Decimal!
  cost: Decimal!
  profit: Decimal!
  margin: Float!
  contribution: Float!  # % of total profit
}

type SalesRepPerformance {
  salesRep: SalesRepresentative!
  period: Period!
  totalOrders: Int!
  totalSales: Decimal!
  averageOrderValue: Decimal!
  commissionEarned: Decimal!
  uniqueCustomers: Int!
  rank: Int
}

# Pagination

type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type OrderEdge {
  node: Order!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Queries

```graphql
type Query {
  # ========================================
  # Sales Overview & Trends
  # ========================================

  """
  Get comprehensive sales overview for a period
  Cache TTL: 1 minute
  """
  salesOverview(
    dateRange: DateRangeInput
    period: Period = MONTH
  ): SalesOverview!

  """
  Get sales trends over time
  Cache TTL: 3 minutes
  """
  salesTrends(
    period: Period!
    metric: Metric!
    dateRange: DateRangeInput
  ): [TrendPoint!]!

  """
  Get real-time metrics (updated every 30 seconds)
  Cache TTL: 30 seconds
  """
  realtimeMetrics: SalesOverview!

  # ========================================
  # Product Analytics
  # ========================================

  """
  Get top performing products
  Cache TTL: 5 minutes
  """
  topProducts(
    limit: Int = 10
    sortBy: ProductSort = REVENUE_DESC
    period: Period = MONTH
    filters: ProductFilterInput
  ): [ProductInsight!]!

  """
  Get detailed product performance
  Cache TTL: 5 minutes
  """
  productPerformance(
    productId: UUID!
    period: Period = MONTH
  ): ProductPerformance!

  """
  Get category breakdown
  Cache TTL: 5 minutes
  """
  categoryBreakdown(
    period: Period = MONTH
  ): [CategoryInsight!]!

  """
  Get category performance details
  Cache TTL: 5 minutes
  """
  categoryPerformance(
    categoryId: UUID!
    period: Period = MONTH
  ): CategoryPerformance!

  """
  Search products by name
  """
  searchProducts(
    query: String!
    limit: Int = 20
  ): [Product!]!

  # ========================================
  # Customer Analytics
  # ========================================

  """
  Get customer segments summary
  Cache TTL: 10 minutes
  """
  customerSegments: [CustomerSegmentSummary!]!

  """
  Get customer lifetime value and metrics
  Cache TTL: 10 minutes
  """
  customerMetrics(
    customerId: UUID!
    period: Period = YEAR
  ): CustomerMetrics!

  """
  Get retention metrics
  Cache TTL: 10 minutes
  """
  customerRetention(
    period: Period = MONTH
  ): CustomerRetentionMetrics!

  """
  Get top customers by lifetime value
  Cache TTL: 10 minutes
  """
  topCustomers(
    limit: Int = 10
    period: Period = YEAR
  ): [CustomerMetrics!]!

  # ========================================
  # Profitability Analysis
  # ========================================

  """
  Get profitability metrics
  Cache TTL: 5 minutes
  """
  profitabilityMetrics(
    period: Period = MONTH
  ): ProfitabilityMetrics!

  """
  Get margin analysis grouped by different dimensions
  Cache TTL: 5 minutes
  """
  marginAnalysis(
    groupBy: GroupBy!
    period: Period = MONTH
    limit: Int = 20
  ): [MarginAnalysis!]!

  # ========================================
  # Sales Representative Performance
  # ========================================

  """
  Get top performing sales reps
  Cache TTL: 10 minutes
  """
  topSalesReps(
    limit: Int = 10
    period: Period = MONTH
  ): [SalesRepPerformance!]!

  """
  Get sales rep performance details
  Cache TTL: 10 minutes
  """
  salesRepPerformance(
    salesRepId: UUID!
    period: Period = MONTH
  ): SalesRepPerformance!

  # ========================================
  # Direct Entity Access
  # ========================================

  product(id: UUID!): Product
  customer(id: UUID!): Customer
  order(id: UUID!): Order
  category(id: UUID!): Category
  salesRep(id: UUID!): SalesRepresentative

  # List queries with filters
  products(
    filters: ProductFilterInput
    pagination: PaginationInput
  ): [Product!]!

  customers(
    filters: CustomerFilterInput
    pagination: PaginationInput
  ): [Customer!]!

  orders(
    filters: OrderFilterInput
    pagination: PaginationInput
  ): OrderConnection!
}
```

---

## Example Queries

### 1. Dashboard Overview

```graphql
query DashboardOverview {
  salesOverview(period: MONTH) {
    totalRevenue
    totalOrders
    averageOrderValue
    uniqueCustomers
    revenueChangePercentage
    ordersChangePercentage
    totalProfit
    profitMargin
  }

  realtimeMetrics {
    totalRevenue
    totalOrders
  }

  topProducts(limit: 5) {
    product {
      id
      name
      sellingPrice
    }
    revenue
    unitsSold
    profit
    profitMargin
    growthRate
  }

  customerSegments {
    segment
    customerCount
    totalRevenue
    averageLifetimeValue
    percentage
  }
}
```

### 2. Sales Trends

```graphql
query SalesTrends($period: Period!, $metric: Metric!) {
  salesTrends(period: $period, metric: $metric) {
    timestamp
    value
    label
    change
    metadata {
      orderCount
      customerCount
      averageOrderValue
    }
  }
}

# Variables:
{
  "period": "MONTH",
  "metric": "REVENUE"
}
```

### 3. Product Performance Deep Dive

```graphql
query ProductDeepDive($productId: UUID!) {
  productPerformance(productId: $productId, period: YEAR) {
    product {
      name
      category {
        name
      }
      costPrice
      sellingPrice
      stockQuantity
    }
    revenue
    unitsSold
    profit
    profitMarginPercentage
    growthRate
    firstSaleDate
    lastSaleDate
  }

  # Get trends for this product
  product(id: $productId) {
    trends(period: MONTH, metric: REVENUE) {
      timestamp
      value
      change
    }
  }
}
```

### 4. Customer Analytics

```graphql
query CustomerAnalytics {
  customerRetention(period: MONTH) {
    newCustomers
    returningCustomers
    churnedCustomers
    retentionRate
    churnRate
    repeatPurchaseRate
  }

  topCustomers(limit: 10) {
    customer {
      name
      email
      segment
    }
    orderCount
    totalSpent
    averageOrderValue
    lastOrderDate
    rfmScore
  }

  customerSegments {
    segment
    customerCount
    totalRevenue
    averageLifetimeValue
  }
}
```

### 5. Profitability Analysis

```graphql
query ProfitabilityAnalysis {
  profitabilityMetrics(period: MONTH) {
    totalRevenue
    totalCost
    totalProfit
    profitMargin

    byCategory {
      category {
        name
      }
      revenue
      profit
      margin
    }
  }

  marginAnalysis(groupBy: CATEGORY, period: MONTH) {
    groupName
    revenue
    profit
    margin
    contribution
  }
}
```

### 6. Sales Rep Leaderboard

```graphql
query SalesRepLeaderboard {
  topSalesReps(limit: 10, period: MONTH) {
    salesRep {
      name
      region
      commissionRate
    }
    totalOrders
    totalSales
    averageOrderValue
    commissionEarned
    uniqueCustomers
    rank
  }
}
```

### 7. Category Performance

```graphql
query CategoryPerformance($categoryId: UUID!) {
  categoryPerformance(categoryId: $categoryId, period: MONTH) {
    category {
      name
      parent {
        name
      }
    }
    revenue
    profit
    unitsSold
    productCount

    topProducts {
      product {
        name
      }
      revenue
      unitsSold
      profit
    }
  }
}
```

---

## Response Times & Caching

| Query | Cache TTL | Expected Response Time |
|-------|-----------|------------------------|
| `salesOverview` | 60s | < 50ms (cached), < 500ms (uncached) |
| `realtimeMetrics` | 30s | < 100ms |
| `salesTrends` | 180s | < 250ms |
| `topProducts` | 300s | < 300ms |
| `customerSegments` | 600s | < 400ms |
| `profitabilityMetrics` | 300s | < 350ms |
| `topSalesReps` | 600s | < 300ms |

---

## Error Handling

### Error Response Format

```json
{
  "errors": [
    {
      "message": "Product not found",
      "extensions": {
        "code": "NOT_FOUND",
        "productId": "123e4567-e89b-12d3-a456-426614174000"
      }
    }
  ],
  "data": null
}
```

### Error Codes

- `UNAUTHENTICATED` - Missing or invalid authentication
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `BAD_USER_INPUT` - Invalid input data
- `INTERNAL_SERVER_ERROR` - Server error
- `QUERY_TOO_COMPLEX` - Query exceeds complexity limit
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## Rate Limiting

- **Anonymous**: 100 requests / minute
- **Authenticated**: 1000 requests / minute
- **Premium**: 5000 requests / minute

Rate limit headers included in response:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

---

## GraphQL Playground

Access the interactive GraphQL Playground at:
- Development: http://localhost:8000/graphql
- Includes auto-complete, documentation explorer, and query history

---

## Best Practices

1. **Request only needed fields** - GraphQL allows you to request exactly what you need
2. **Use fragments** for reusable field sets
3. **Leverage caching** - Identical queries return cached results
4. **Batch queries** - Combine multiple queries in one request
5. **Use variables** - Don't concatenate strings for query parameters
6. **Handle errors gracefully** - Check both `data` and `errors` in response
7. **Monitor complexity** - Keep queries under complexity limit

---

## GraphQL Fragments Example

```graphql
fragment ProductDetails on Product {
  id
  name
  sellingPrice
  stockQuantity
  category {
    name
  }
}

fragment PerformanceMetrics on ProductPerformance {
  revenue
  unitsSold
  profit
  profitMarginPercentage
  growthRate
}

query ProductsWithPerformance {
  topProducts(limit: 10) {
    product {
      ...ProductDetails
    }
    ...PerformanceMetrics
  }
}
```

---

For implementation details, see:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - Step-by-step guide
- [FRONTEND.md](./FRONTEND.md) - Frontend integration
