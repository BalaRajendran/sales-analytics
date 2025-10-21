#!/bin/bash

# Automated GraphQL Query Testing Script
# Tests all GraphQL queries and generates a summary report

BASE_URL="http://localhost:8000/graphql"
LOG_CONTAINER="shopx-analytics-api"
RESULTS_FILE="test_results.md"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Initialize results
total_tests=0
passed_tests=0
failed_tests=0

# Initialize results file
cat > "$RESULTS_FILE" << EOF
# GraphQL Queries Test Results
**Date:** $(date)
**Server:** $BASE_URL

---

EOF

# Function to test a query and log results
test_query() {
    local query_name=$1
    local query_payload=$2

    ((total_tests++))

    echo -e "\n${YELLOW}Testing: $query_name${NC}"

    # Clear logs before test
    log_marker="TEST_${total_tests}_START"

    # Execute query
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -d "$query_payload")

    # Check for errors
    has_errors=$(echo "$response" | jq -e '.errors' > /dev/null 2>&1 && echo "true" || echo "false")
    has_data=$(echo "$response" | jq -e '.data' > /dev/null 2>&1 && echo "true" || echo "false")

    # Get logs after query
    logs=$(docker logs "$LOG_CONTAINER" --tail 50 2>&1 | tail -20)
    errors_in_logs=$(echo "$logs" | grep -i "error" | grep -v "0 errors" || echo "")

    # Determine test result
    if [ "$has_errors" = "false" ] && [ "$has_data" = "true" ] && [ -z "$errors_in_logs" ]; then
        ((passed_tests++))
        status="✅ PASSED"
        status_color=$GREEN
    else
        ((failed_tests++))
        status="❌ FAILED"
        status_color=$RED
    fi

    echo -e "${status_color}$status${NC}"

    # Log to results file
    cat >> "$RESULTS_FILE" << EOF
## $total_tests. $query_name
**Status:** $status

### Response Summary
- Has Data: $has_data
- Has Errors: $has_errors

EOF

    if [ "$has_errors" = "true" ]; then
        cat >> "$RESULTS_FILE" << EOF
### GraphQL Errors
\`\`\`json
$(echo "$response" | jq '.errors' 2>/dev/null || echo "Could not parse errors")
\`\`\`

EOF
    fi

    if [ -n "$errors_in_logs" ]; then
        cat >> "$RESULTS_FILE" << EOF
### Server Logs (Errors Found)
\`\`\`
$errors_in_logs
\`\`\`

EOF
    else
        cat >> "$RESULTS_FILE" << EOF
### Server Logs
No errors found in logs.

EOF
    fi

    # Sample of response data
    cat >> "$RESULTS_FILE" << EOF
### Response Data (Sample)
\`\`\`json
$(echo "$response" | jq '.data' 2>/dev/null | head -20 || echo "Could not parse response")
\`\`\`

---

EOF
}

echo -e "${YELLOW}==================================${NC}"
echo -e "${YELLOW}GraphQL Queries Test Suite${NC}"
echo -e "${YELLOW}==================================${NC}"

# Test 1: Dashboard Overview
test_query "Dashboard Overview" '{
  "operationName": "GetDashboardOverview",
  "variables": {"dateRange": "LAST_7_DAYS"},
  "query": "query GetDashboardOverview($dateRange: DateRangeEnum = LAST_7_DAYS) { dashboardOverview(dateRange: $dateRange) { revenueMetrics { totalRevenue totalProfit profitMarginPercentage } orderMetrics { totalOrders completedOrders pendingOrders cancelledOrders avgOrderValue } topProducts { productId productName categoryName timesSold totalRevenue } topCategories { categoryId categoryName productsCount totalRevenue } dateRange startDate endDate } }"
}'

# Test 2: Realtime Metrics
test_query "Realtime Metrics" '{
  "query": "query { realtimeMetrics { activeUsers pendingOrders revenueToday ordersToday avgOrderValueToday timestamp } }"
}'

# Test 3: Products List
test_query "Products List (Paginated)" '{
  "variables": {"limit": 10, "offset": 0},
  "query": "query GetProducts($limit: Int, $offset: Int) { products(limit: $limit, offset: $offset) { edges { id name sellingPrice stockQuantity profitMarginPercentage category { name } } pageInfo { hasNextPage hasPreviousPage totalCount } } }"
}'

# Test 4: Product Performance
test_query "Product Performance" '{
  "variables": {"dateRange": "LAST_30_DAYS", "limit": 10},
  "query": "query GetProductPerformance($dateRange: DateRangeEnum, $limit: Int) { productPerformance(dateRange: $dateRange, limit: $limit) { productId productName categoryName timesSold totalRevenue totalProfit profitMarginPercentage stockQuantity revenueRank } }"
}'

# Test 5: Customers List
test_query "Customers List (Paginated)" '{
  "variables": {"limit": 10, "offset": 0},
  "query": "query GetCustomers($limit: Int, $offset: Int) { customers(limit: $limit, offset: $offset) { edges { id name email segment totalLifetimeValue } pageInfo { hasNextPage hasPreviousPage totalCount } } }"
}'

# Test 6: Customer Segment Distribution
test_query "Customer Segment Distribution" '{
  "query": "query { customerSegmentDistribution { segment customerCount totalRevenue avgLifetimeValue percentage } }"
}'

# Test 7: Orders List
test_query "Orders List (Paginated)" '{
  "variables": {"limit": 10, "offset": 0},
  "query": "query GetOrders($limit: Int, $offset: Int) { orders(limit: $limit, offset: $offset) { edges { id orderDate totalAmount status profit customerId salesRepId } pageInfo { hasNextPage hasPreviousPage totalCount } } }"
}'

# Test 8: Profit Analysis
test_query "Profit Analysis" '{
  "variables": {"dateRange": "LAST_30_DAYS"},
  "query": "query GetProfitAnalysis($dateRange: DateRangeEnum) { profitAnalysis(dateRange: $dateRange) { totalRevenue totalCost totalProfit profitMarginPercentage } }"
}'

# Test 9: Regional Performance
test_query "Regional Performance" '{
  "variables": {"dateRange": "LAST_30_DAYS"},
  "query": "query GetRegionalPerformance($dateRange: DateRangeEnum) { regionalPerformance(dateRange: $dateRange) { region totalRevenue totalOrders salesRepsCount avgOrderValue revenueContributionPercentage } }"
}'

# Test 10: Cache Info
test_query "Cache Info" '{
  "query": "query { cacheInfo { cacheHits cacheMisses hitRatePercentage isCached } }"
}'

# Generate summary
cat >> "$RESULTS_FILE" << EOF

---

# Summary

**Total Tests:** $total_tests
**Passed:** ✅ $passed_tests
**Failed:** ❌ $failed_tests
**Success Rate:** $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc)%

## Test Status Overview

EOF

echo -e "\n${YELLOW}==================================${NC}"
echo -e "${YELLOW}Test Summary${NC}"
echo -e "${YELLOW}==================================${NC}"
echo -e "Total Tests: $total_tests"
echo -e "${GREEN}Passed: $passed_tests${NC}"
echo -e "${RED}Failed: $failed_tests${NC}"
echo -e "Success Rate: $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc)%"
echo -e "\n${YELLOW}Detailed results saved to: $RESULTS_FILE${NC}"

# Open results file
if command -v open &> /dev/null; then
    echo -e "${YELLOW}Opening results file...${NC}"
    open "$RESULTS_FILE"
fi
