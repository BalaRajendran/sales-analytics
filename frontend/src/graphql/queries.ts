/**
 * GraphQL Queries
 *
 * All queries for fetching data from the Sales Dashboard API.
 */

import { gql } from '@apollo/client';

// ============================================================================
// DASHBOARD QUERIES
// ============================================================================

export const GET_DASHBOARD_OVERVIEW = gql`
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
`;

// ============================================================================
// PRODUCT QUERIES
// ============================================================================

export const GET_ALL_PRODUCTS = gql`
  query GetAllProducts($limit: Int = 20, $offset: Int = 0, $filter: ProductFilter) {
    products(limit: $limit, offset: $offset, filter: $filter) {
      edges {
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
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        totalCount
      }
    }
  }
`;

export const GET_PRODUCT = gql`
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
`;

export const GET_PRODUCT_PERFORMANCE = gql`
  query GetProductPerformance($dateRange: DateRangeEnum = LAST_30_DAYS, $limit: Int = 10) {
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
`;

// ============================================================================
// CUSTOMER QUERIES
// ============================================================================

export const GET_ALL_CUSTOMERS = gql`
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
`;

export const GET_CUSTOMER = gql`
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
`;

export const GET_CUSTOMER_SEGMENTS = gql`
  query GetCustomerSegments {
    customerSegmentDistribution {
      segment
      customerCount
      totalRevenue
      avgLifetimeValue
      percentage
    }
  }
`;

// ============================================================================
// ORDER QUERIES
// ============================================================================

export const GET_ALL_ORDERS = gql`
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
`;

export const GET_ORDER = gql`
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
`;

// ============================================================================
// ANALYTICS QUERIES (ADDITIONAL)
// ============================================================================

export const GET_REALTIME_METRICS = gql`
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
`;

export const GET_PROFIT_ANALYSIS = gql`
  query GetProfitAnalysis($dateRange: DateRangeEnum = LAST_30_DAYS) {
    profitAnalysis(dateRange: $dateRange) {
      totalRevenue
      totalCost
      totalProfit
      profitMarginPercentage
    }
  }
`;

export const GET_CACHE_INFO = gql`
  query GetCacheInfo {
    cacheInfo {
      cacheHits
      cacheMisses
      hitRatePercentage
      isCached
    }
  }
`;

