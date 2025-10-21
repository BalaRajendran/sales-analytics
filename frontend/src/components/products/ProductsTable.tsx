/**
 * ProductsTable Component
 *
 * Table displaying all products with actions.
 */

import { formatCurrency, formatNumber } from '../../utils/dateHelpers';

interface Product {
  id: string;
  name: string;
  categoryId: string;
  costPrice: number;
  sellingPrice: number;
  stockQuantity: number;
  profitMargin: number;
  profitMarginPercentage: number;
  createdAt: string;
  updatedAt: string;
  category?: {
    id: string;
    name: string;
  } | null;
}

interface ProductsTableProps {
  products: Product[];
  loading?: boolean;
}

function ProductsTable({ products, loading = false }: ProductsTableProps) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Price
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Stock
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => {
              const isLowStock = product.stockQuantity < 10;
              const inStock = product.stockQuantity > 0;

              return (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{product.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-600">
                      {product.category?.name || 'Uncategorized'}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="text-sm font-semibold text-gray-900">
                      {formatCurrency(product.sellingPrice)}
                    </div>
                    <div className="text-xs text-green-600">
                      {product.profitMarginPercentage.toFixed(1)}% margin
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="text-sm text-gray-600">{formatCurrency(product.costPrice)}</div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div
                      className={`text-sm font-medium ${
                        isLowStock ? 'text-red-600' : 'text-gray-900'
                      }`}
                    >
                      {formatNumber(product.stockQuantity)}
                    </div>
                    {isLowStock && (
                      <div className="text-xs text-red-600">Low Stock!</div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {inStock ? (
                      <span className="badge-success">In Stock</span>
                    ) : (
                      <span className="badge-gray">Out of Stock</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-primary-600 hover:text-primary-900 text-sm font-medium mr-3">
                      Edit
                    </button>
                    <button className="text-red-600 hover:text-red-900 text-sm font-medium">
                      Delete
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {products.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No products found</p>
          <p className="text-sm">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}

export default ProductsTable;
