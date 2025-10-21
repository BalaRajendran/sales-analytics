/**
 * TopProductsTable Component
 *
 * Table showing top-selling products.
 */

import { formatCurrency, formatNumber } from '../../utils/dateHelpers';

interface TopProduct {
  productId: number;
  productName: string;
  revenue: number;
  unitsSold: number;
  avgPrice: number;
}

interface TopProductsTableProps {
  products: TopProduct[];
  loading?: boolean;
}

function TopProductsTable({ products, loading = false }: TopProductsTableProps) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 bg-gray-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Products</h3>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Revenue
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Units Sold
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Price
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product, index) => (
              <tr key={product.productId} className="hover:bg-gray-50">
                <td className="px-4 py-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-primary-700">
                        {index + 1}
                      </span>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{product.productName}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4 text-right">
                  <p className="text-sm font-semibold text-gray-900">
                    {formatCurrency(product.revenue)}
                  </p>
                </td>
                <td className="px-4 py-4 text-right">
                  <p className="text-sm text-gray-900">{formatNumber(product.unitsSold)}</p>
                </td>
                <td className="px-4 py-4 text-right">
                  <p className="text-sm text-gray-600">{formatCurrency(product.avgPrice)}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {products.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No products data available
        </div>
      )}
    </div>
  );
}

export default TopProductsTable;
