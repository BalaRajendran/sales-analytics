/**
 * Dashboard Page
 *
 * Main dashboard with analytics overview.
 */

import { useState } from 'react';
import { useQuery } from '@apollo/client';
import {
  CurrencyDollarIcon,
  ShoppingCartIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';

import { GET_DASHBOARD_OVERVIEW } from '../graphql/queries';
import {
  type DateRangeKey,
  formatCurrency,
  formatNumber,
  formatPercentage,
} from '../utils/dateHelpers';

import StatCard from '../components/dashboard/StatCard';
import RevenueChart from '../components/dashboard/RevenueChart';
import TopProductsTable from '../components/dashboard/TopProductsTable';
import DateRangeSelector from '../components/dashboard/DateRangeSelector';

function Dashboard() {
  const [selectedRange, setSelectedRange] = useState<DateRangeKey>('30d');

  // Map frontend date range to backend enum
  const mapDateRange = (range: DateRangeKey): string => {
    const rangeMap: Record<DateRangeKey, string> = {
      '7d': 'LAST_7_DAYS',
      '30d': 'LAST_30_DAYS',
      '90d': 'LAST_90_DAYS',
      '1y': 'THIS_YEAR',
    };
    return rangeMap[range] || 'LAST_30_DAYS';
  };

  // Fetch dashboard data
  const { data, loading, error } = useQuery(GET_DASHBOARD_OVERVIEW, {
    variables: {
      dateRange: mapDateRange(selectedRange),
    },
  });

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Dashboard</h3>
        <p className="text-red-600 text-sm">{error.message}</p>
        <p className="text-red-500 text-xs mt-2">
          Make sure the backend API is running at http://localhost:8000/graphql
        </p>
      </div>
    );
  }

  // Extract data from response
  const dashboard = data?.dashboardOverview;
  const revenueMetrics = dashboard?.revenueMetrics || {};
  const orderMetrics = dashboard?.orderMetrics || {};
  const topProducts = (dashboard?.topProducts || []).map((product: any) => ({
    productId: product.productId,
    productName: product.productName,
    revenue: parseFloat(product.totalRevenue || 0),
    unitsSold: product.timesSold || 0,
    avgPrice: product.timesSold > 0 ? parseFloat(product.totalRevenue || 0) / product.timesSold : 0,
  }));

  // Transform revenue trend data for the chart
  const revenueTrendData = (dashboard?.revenueTrend?.dataPoints || []).map((point: any) => ({
    date: point.date,
    revenue: parseFloat(point.value || 0),
    ordersCount: 0, // Order count not available in revenue trend, would need orderTrend
  }));

  // Get order trend data if available
  const orderTrendData = dashboard?.orderTrend?.dataPoints || [];

  // Merge revenue and order trends by date
  const revenueTrend = revenueTrendData.map((revenuePoint: any, index: number) => ({
    ...revenuePoint,
    ordersCount: orderTrendData[index] ? parseFloat(orderTrendData[index].value || 0) : 0,
  }));

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="text-sm text-gray-600 mt-1">
            Real-time analytics and performance metrics
          </p>
        </div>
        <DateRangeSelector selectedRange={selectedRange} onRangeChange={setSelectedRange} />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          label="Total Revenue"
          value={formatCurrency(revenueMetrics.totalRevenue || 0)}
          change={revenueMetrics.revenueGrowth}
          icon={CurrencyDollarIcon}
          loading={loading}
        />
        <StatCard
          label="Total Orders"
          value={formatNumber(orderMetrics.totalOrders || 0)}
          icon={ShoppingCartIcon}
          loading={loading}
        />
        <StatCard
          label="Average Order Value"
          value={formatCurrency(orderMetrics.avgOrderValue || 0)}
          icon={ChartBarIcon}
          loading={loading}
        />
        <StatCard
          label="Profit Margin"
          value={formatPercentage(revenueMetrics.profitMarginPercentage || 0)}
          icon={ArrowTrendingUpIcon}
          loading={loading}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Revenue Trend Chart - Spans 2 columns */}
        <div className="lg:col-span-2">
          <RevenueChart data={revenueTrend} loading={loading} />
        </div>

        {/* Quick Stats */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Completed Orders</p>
              <p className="text-2xl font-bold text-green-600">
                {loading ? '...' : formatNumber(orderMetrics.completedOrders || 0)}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Pending Orders</p>
              <p className="text-2xl font-bold text-yellow-600">
                {loading ? '...' : formatNumber(orderMetrics.pendingOrders || 0)}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Cancelled Orders</p>
              <p className="text-2xl font-bold text-red-600">
                {loading ? '...' : formatNumber(orderMetrics.cancelledOrders || 0)}
              </p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Data refreshed in real-time from Redis cache
            </p>
          </div>
        </div>
      </div>

      {/* Top Products Table */}
      <TopProductsTable products={topProducts} loading={loading} />
    </div>
  );
}

export default Dashboard;
