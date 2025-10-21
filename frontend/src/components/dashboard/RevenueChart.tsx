/**
 * RevenueChart Component
 *
 * Line chart showing revenue trend over time.
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatCurrency, formatForDisplay } from '../../utils/dateHelpers';

interface RevenueTrendData {
  date: string;
  revenue: number;
  ordersCount: number;
}

interface RevenueChartProps {
  data: RevenueTrendData[];
  loading?: boolean;
}

function RevenueChart({ data, loading = false }: RevenueChartProps) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-64 bg-gray-100 rounded"></div>
      </div>
    );
  }

  // Format data for the chart
  const chartData = data.map((item) => ({
    date: formatForDisplay(item.date, 'MMM d'),
    revenue: item.revenue,
    orders: item.ordersCount,
  }));

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            stroke="#6b7280"
            style={{ fontSize: 12 }}
          />
          <YAxis
            stroke="#6b7280"
            style={{ fontSize: 12 }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            formatter={(value: number, name: string) => {
              if (name === 'revenue') return [formatCurrency(value), 'Revenue'];
              return [value, 'Orders'];
            }}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ fill: '#2563eb', r: 4 }}
            activeDot={{ r: 6 }}
            name="Revenue"
          />
          <Line
            type="monotone"
            dataKey="orders"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 4 }}
            activeDot={{ r: 6 }}
            name="Orders"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RevenueChart;
