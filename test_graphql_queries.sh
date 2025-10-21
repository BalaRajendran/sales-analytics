#!/bin/bash

# GraphQL Query Testing Script
# Tests all GraphQL queries and checks FastAPI logs for errors

BASE_URL="http://localhost:8000/graphql"
LOG_CONTAINER="shopx-analytics-api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}\n"
}

# Function to test a GraphQL query
test_query() {
    local query_name=$1
    local query_payload=$2

    print_header "Testing: $query_name"

    echo "Request:"
    echo "$query_payload" | jq . 2>/dev/null || echo "$query_payload"
    echo ""

    # Execute the query
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -d "$query_payload")

    echo -e "\n${GREEN}Response:${NC}"
    echo "$response" | jq . 2>/dev/null || echo "$response"

    # Check for errors in response
    if echo "$response" | jq -e '.errors' > /dev/null 2>&1; then
        echo -e "\n${RED}✗ Query returned errors${NC}"
    else
        echo -e "\n${GREEN}✓ Query executed successfully${NC}"
    fi

    # Check logs
    echo -e "\n${YELLOW}Recent Logs:${NC}"
    docker logs "$LOG_CONTAINER" --tail 10 2>&1 | grep -E "(ERROR|WARN|INFO.*graphql)" || echo "No relevant log entries"

    echo -e "\n${YELLOW}Press Enter to continue...${NC}"
    read
}

# 1. Dashboard Overview
test_query "Dashboard Overview" '{
  "operationName": "GetDashboardOverview",
  "variables": {
    "dateRange": "LAST_7_DAYS"
  },
  "query": "query GetDashboardOverview($dateRange: DateRangeEnum = LAST_7_DAYS) {\n  dashboardOverview(dateRange: $dateRange) {\n    revenueMetrics {\n      totalRevenue\n      totalProfit\n      profitMarginPercentage\n      revenueGrowth\n      __typename\n    }\n    orderMetrics {\n      totalOrders\n      completedOrders\n      pendingOrders\n      cancelledOrders\n      avgOrderValue\n      __typename\n    }\n    topProducts {\n      productId\n      productName\n      categoryName\n      timesSold\n      totalRevenue\n      totalProfit\n      stockQuantity\n      __typename\n    }\n    topCategories {\n      categoryId\n      categoryName\n      productsCount\n      totalRevenue\n      totalProfit\n      revenueContributionPercentage\n      __typename\n    }\n    revenueTrend {\n      period\n      dataPoints {\n        date\n        value\n        label\n        __typename\n      }\n      total\n      average\n      trendDirection\n      __typename\n    }\n    orderTrend {\n      period\n      dataPoints {\n        date\n        value\n        label\n        __typename\n      }\n      total\n      average\n      trendDirection\n      __typename\n    }\n    dateRange\n    startDate\n    endDate\n    __typename\n  }\n}"
}'

# 2. Realtime Metrics
test_query "Realtime Metrics" '{
  "operationName": "GetRealtimeMetrics",
  "query": "query GetRealtimeMetrics {\n  realtimeMetrics {\n    activeUsers\n    pendingOrders\n    revenueToday\n    ordersToday\n    avgOrderValueToday\n    timestamp\n    __typename\n  }\n}"
}'

# 3. Products List
test_query "Products List" '{
  "operationName": "GetProducts",
  "variables": {
    "limit": 10,
    "offset": 0
  },
  "query": "query GetProducts($limit: Int = 10, $offset: Int = 0, $filter: ProductFilter) {\n  products(limit: $limit, offset: $offset, filter: $filter) {\n    edges {\n      id\n      name\n      sellingPrice\n      stockQuantity\n      profitMarginPercentage\n      category {\n        name\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      totalCount\n      __typename\n    }\n    __typename\n  }\n}"
}'

# 4. Product Performance
test_query "Product Performance" '{
  "operationName": "GetProductPerformance",
  "variables": {
    "dateRange": "LAST_30_DAYS",
    "limit": 10
  },
  "query": "query GetProductPerformance($dateRange: DateRangeEnum = LAST_30_DAYS, $limit: Int = 10) {\n  productPerformance(dateRange: $dateRange, limit: $limit) {\n    productId\n    productName\n    categoryName\n    timesSold\n    totalRevenue\n    totalProfit\n    profitMarginPercentage\n    stockQuantity\n    revenueRank\n    __typename\n  }\n}"
}'

# 5. Customers List
test_query "Customers List" '{
  "operationName": "GetCustomers",
  "variables": {
    "limit": 10,
    "offset": 0
  },
  "query": "query GetCustomers($limit: Int = 10, $offset: Int = 0, $filter: CustomerFilter) {\n  customers(limit: $limit, offset: $offset, filter: $filter) {\n    edges {\n      id\n      name\n      email\n      segment\n      totalLifetimeValue\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      totalCount\n      __typename\n    }\n    __typename\n  }\n}"
}'

# 6. Customer Segment Distribution
test_query "Customer Segment Distribution" '{
  "operationName": "GetCustomerSegments",
  "query": "query GetCustomerSegments {\n  customerSegmentDistribution {\n    segment\n    customerCount\n    totalRevenue\n    avgLifetimeValue\n    percentage\n    __typename\n  }\n}"
}'

# 7. Orders List
test_query "Orders List" '{
  "operationName": "GetOrders",
  "variables": {
    "limit": 10,
    "offset": 0
  },
  "query": "query GetOrders($limit: Int = 10, $offset: Int = 0, $filter: OrderFilter) {\n  orders(limit: $limit, offset: $offset, filter: $filter) {\n    edges {\n      id\n      orderDate\n      totalAmount\n      status\n      profit\n      customerId\n      salesRepId\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      totalCount\n      __typename\n    }\n    __typename\n  }\n}"
}'

# 8. Profit Analysis
test_query "Profit Analysis" '{
  "operationName": "GetProfitAnalysis",
  "variables": {
    "dateRange": "LAST_30_DAYS"
  },
  "query": "query GetProfitAnalysis($dateRange: DateRangeEnum = LAST_30_DAYS) {\n  profitAnalysis(dateRange: $dateRange) {\n    totalRevenue\n    totalCost\n    totalProfit\n    profitMarginPercentage\n    __typename\n  }\n}"
}'

# 9. Regional Performance
test_query "Regional Performance" '{
  "operationName": "GetRegionalPerformance",
  "variables": {
    "dateRange": "LAST_30_DAYS"
  },
  "query": "query GetRegionalPerformance($dateRange: DateRangeEnum = LAST_30_DAYS) {\n  regionalPerformance(dateRange: $dateRange) {\n    region\n    totalRevenue\n    totalOrders\n    salesRepsCount\n    avgOrderValue\n    revenueContributionPercentage\n    __typename\n  }\n}"
}'

# 10. Cache Info
test_query "Cache Info" '{
  "operationName": "GetCacheInfo",
  "query": "query GetCacheInfo {\n  cacheInfo {\n    cacheHits\n    cacheMisses\n    hitRatePercentage\n    isCached\n    __typename\n  }\n}"
}'

print_header "All Tests Completed"
echo "Check the logs above for any errors or warnings"
