/**
 * Sales Reps Page
 *
 * Sales representatives leaderboard and performance tracking.
 */

import { useState } from 'react';
import { useQuery } from '@apollo/client';
import { GET_DASHBOARD_OVERVIEW } from '../graphql/queries';

import DateRangeSelector from '../components/dashboard/DateRangeSelector';
import SalesRepsLeaderboard from '../components/salesreps/SalesRepsLeaderboard';

// Map date range keys to DateRangeEnum
const dateRangeMap: Record<string, string> = {
  '7d': 'LAST_7_DAYS',
  '30d': 'LAST_30_DAYS',
  '90d': 'LAST_90_DAYS',
};

function SalesReps() {
  const [selectedRange, setSelectedRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  // Fetch dashboard which includes top sales reps
  const { data, loading } = useQuery(GET_DASHBOARD_OVERVIEW, {
    variables: {
      dateRange: dateRangeMap[selectedRange] || 'LAST_30_DAYS',
    },
  });

  const salesReps = data?.dashboardOverview?.topSalesReps || [];

  // Calculate totals from sales reps data
  const totalRevenue = salesReps.reduce((sum: number, rep: any) => sum + parseFloat(rep.totalSales || 0), 0);
  const totalOrders = salesReps.reduce((sum: number, rep: any) => sum + (rep.totalOrders || 0), 0);
  const avgRevenue = salesReps.length > 0 ? totalRevenue / salesReps.length : 0;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sales Representatives</h1>
          <p className="text-sm text-gray-600 mt-1">
            Performance leaderboard and team metrics
          </p>
        </div>
        <DateRangeSelector selectedRange={selectedRange} onRangeChange={setSelectedRange} />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="stat-card">
          <p className="stat-label">Total Team Revenue</p>
          <p className="stat-value">
            {loading ? '...' : `$${(totalRevenue / 1000).toFixed(0)}k`}
          </p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Total Team Orders</p>
          <p className="stat-value">{loading ? '...' : totalOrders.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Avg Revenue per Rep</p>
          <p className="stat-value">{loading ? '...' : `$${(avgRevenue / 1000).toFixed(1)}k`}</p>
        </div>
      </div>

      {/* Leaderboard */}
      <SalesRepsLeaderboard salesReps={salesReps} loading={loading} />
    </div>
  );
}

export default SalesReps;
