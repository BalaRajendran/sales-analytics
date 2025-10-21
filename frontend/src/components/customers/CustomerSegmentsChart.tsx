/**
 * CustomerSegmentsChart Component
 *
 * Pie chart showing customer distribution by segment.
 */

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { formatCurrency } from '../../utils/dateHelpers';

interface CustomerSegment {
  segment: string;
  count: number;
  totalRevenue: number;
  avgLifetimeValue: number;
}

interface CustomerSegmentsChartProps {
  segments: CustomerSegment[];
  loading?: boolean;
}

const SEGMENT_COLORS: Record<string, string> = {
  premium: '#10b981',
  regular: '#3b82f6',
  new: '#f59e0b',
  'at-risk': '#ef4444',
  churned: '#6b7280',
};

function CustomerSegmentsChart({ segments, loading = false }: CustomerSegmentsChartProps) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-64 bg-gray-100 rounded"></div>
      </div>
    );
  }

  // Format data for pie chart
  const chartData = segments.map((segment) => ({
    name: segment.segment.charAt(0).toUpperCase() + segment.segment.slice(1),
    value: segment.count,
    revenue: segment.totalRevenue,
    avgLTV: segment.avgLifetimeValue,
  }));

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Segments</h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name} (${entry.value})`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={SEGMENT_COLORS[entry.name.toLowerCase()] || '#6b7280'}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'value') return [value, 'Customers'];
                  return [value, name];
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Segment Details */}
        <div className="space-y-4">
          {segments.map((segment) => (
            <div key={segment.segment} className="border-l-4 border-gray-200 pl-4">
              <div className="flex items-center justify-between mb-1">
                <h4 className="text-sm font-semibold text-gray-900 uppercase">
                  {segment.segment}
                </h4>
                <span
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium text-white"
                  style={{
                    backgroundColor: SEGMENT_COLORS[segment.segment] || '#6b7280',
                  }}
                >
                  {segment.count} customers
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Total Revenue:</span>
                <span className="font-semibold text-gray-900">
                  {formatCurrency(segment.totalRevenue)}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Avg LTV:</span>
                <span className="font-medium text-gray-700">
                  {formatCurrency(segment.avgLifetimeValue)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {segments.length === 0 && (
        <div className="text-center py-8 text-gray-500">No segment data available</div>
      )}
    </div>
  );
}

export default CustomerSegmentsChart;
