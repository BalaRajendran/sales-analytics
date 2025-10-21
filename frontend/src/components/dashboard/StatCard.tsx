/**
 * StatCard Component
 *
 * Display a single metric with value, label, and change indicator.
 */

import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

interface StatCardProps {
  label: string;
  value: string;
  change?: number;
  icon?: React.ComponentType<{ className?: string }>;
  loading?: boolean;
}

function StatCard({ label, value, change, icon: Icon, loading = false }: StatCardProps) {
  const isPositive = change !== undefined && change >= 0;
  const ChangeIcon = isPositive ? ArrowUpIcon : ArrowDownIcon;

  if (loading) {
    return (
      <div className="stat-card animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-1/3"></div>
      </div>
    );
  }

  return (
    <div className="stat-card">
      <div className="flex items-center justify-between mb-2">
        <p className="stat-label">{label}</p>
        {Icon && <Icon className="h-5 w-5 text-gray-400" />}
      </div>

      <p className="stat-value">{value}</p>

      {change !== undefined && (
        <div className={isPositive ? 'stat-change-positive' : 'stat-change-negative'}>
          <div className="flex items-center">
            <ChangeIcon className="h-4 w-4 mr-1" />
            <span>{Math.abs(change).toFixed(1)}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default StatCard;
