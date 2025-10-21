# GraphQL Queries Test Results
**Date:** Tue Oct 21 11:41:27 IST 2025
**Server:** http://localhost:8000/graphql

---

## 1. Dashboard Overview
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "dashboardOverview": {
    "revenueMetrics": {
      "totalRevenue": "0.00",
      "totalProfit": "0.000",
      "profitMarginPercentage": 30.0
    },
    "orderMetrics": {
      "totalOrders": 0,
      "completedOrders": 0,
      "pendingOrders": 0,
      "cancelledOrders": 0,
      "avgOrderValue": "0.00"
    },
    "topProducts": [],
    "topCategories": [],
    "dateRange": "7d",
    "startDate": "2025-10-14T06:11:27.052607",
    "endDate": "2025-10-21T06:11:27.052607"
  }
```

---

## 2. Realtime Metrics
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "realtimeMetrics": {
    "activeUsers": 0,
    "pendingOrders": 0,
    "revenueToday": "0.00",
    "ordersToday": 0,
    "avgOrderValueToday": "0.00",
    "timestamp": "2025-10-21T06:11:27.158450"
  }
}
```

---

## 3. Products List (Paginated)
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "products": {
    "edges": [],
    "pageInfo": {
      "hasNextPage": false,
      "hasPreviousPage": false,
      "totalCount": 0
    }
  }
}
```

---

## 4. Product Performance
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "productPerformance": []
}
```

---

## 5. Customers List (Paginated)
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "customers": {
    "edges": [],
    "pageInfo": {
      "hasNextPage": false,
      "hasPreviousPage": false,
      "totalCount": 0
    }
  }
}
```

---

## 6. Customer Segment Distribution
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "customerSegmentDistribution": []
}
```

---

## 7. Orders List (Paginated)
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "orders": {
    "edges": [],
    "pageInfo": {
      "hasNextPage": false,
      "hasPreviousPage": false,
      "totalCount": 0
    }
  }
}
```

---

## 8. Profit Analysis
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "profitAnalysis": {
    "totalRevenue": "0.00",
    "totalCost": "0.00",
    "totalProfit": "0.00",
    "profitMarginPercentage": 0.0
  }
}
```

---

## 9. Regional Performance
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "regionalPerformance": []
}
```

---

## 10. Cache Info
**Status:** ✅ PASSED

### Response Summary
- Has Data: true
- Has Errors: false

### Server Logs
No errors found in logs.

### Response Data (Sample)
```json
{
  "cacheInfo": {
    "cacheHits": 0,
    "cacheMisses": 6,
    "hitRatePercentage": 0.0,
    "isCached": true
  }
}
```

---


---

# Summary

**Total Tests:** 10
**Passed:** ✅ 10
**Failed:** ❌ 0
**Success Rate:** 100.00%

## Test Status Overview

