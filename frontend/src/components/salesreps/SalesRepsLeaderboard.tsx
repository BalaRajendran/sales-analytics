/**
 * SalesRepsLeaderboard Component
 *
 * Leaderboard showing top-performing sales representatives.
 */

import { TrophyIcon } from '@heroicons/react/24/solid';
import { formatCurrency, formatNumber, formatPercentage } from '../../utils/dateHelpers';

interface SalesRep {
  repId: number;
  repName: string;
  totalRevenue: number;
  ordersCount: number;
  conversionRate: number;
}

interface SalesRepsLeaderboardProps {
  salesReps: SalesRep[];
  loading?: boolean;
}

const rankColors = ['text-yellow-500', 'text-gray-400', 'text-orange-600'];

function SalesRepsLeaderboard({ salesReps, loading = false }: SalesRepsLeaderboardProps) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-20 bg-gray-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Sales Leaderboard
      </h3>

      <div className="space-y-4">
        {salesReps.map((rep, index) => {
          const rank = index + 1;
          const isTopThree = rank <= 3;
          const rankColor = isTopThree ? rankColors[rank - 1] : 'text-gray-600';

          return (
            <div
              key={rep.repId}
              className={`p-4 rounded-lg border-2 ${
                isTopThree ? 'bg-gradient-to-r from-gray-50 to-white border-primary-200' : 'bg-white border-gray-200'
              } hover:shadow-md transition-shadow`}
            >
              <div className="flex items-center">
                {/* Rank */}
                <div className={`flex-shrink-0 w-12 text-center ${rankColor}`}>
                  {rank <= 3 ? (
                    <TrophyIcon className="h-8 w-8 mx-auto" />
                  ) : (
                    <div className="text-2xl font-bold">#{rank}</div>
                  )}
                </div>

                {/* Name */}
                <div className="flex-1 ml-4">
                  <h4 className="text-lg font-semibold text-gray-900">{rep.repName}</h4>
                  <p className="text-sm text-gray-500">Rep ID: {rep.repId}</p>
                </div>

                {/* Metrics */}
                <div className="flex items-center space-x-8">
                  {/* Revenue */}
                  <div className="text-right">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Revenue</p>
                    <p className="text-lg font-bold text-green-600">
                      {formatCurrency(rep.totalRevenue)}
                    </p>
                  </div>

                  {/* Orders */}
                  <div className="text-right">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Orders</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatNumber(rep.ordersCount)}
                    </p>
                  </div>

                  {/* Conversion Rate */}
                  <div className="text-right">
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                      Conversion
                    </p>
                    <p className="text-lg font-semibold text-blue-600">
                      {formatPercentage(rep.conversionRate)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Progress Bar (for top 3) */}
              {isTopThree && salesReps[0] && (
                <div className="mt-3">
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full transition-all"
                      style={{
                        width: `${(rep.totalRevenue / salesReps[0].totalRevenue) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {salesReps.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No sales data available</p>
          <p className="text-sm">Check back after some sales are recorded</p>
        </div>
      )}
    </div>
  );
}

export default SalesRepsLeaderboard;
