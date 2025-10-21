/**
 * LowStockAlert Component
 *
 * Alert banner showing low stock products.
 */

import { ExclamationTriangleIcon } from '@heroicons/react/24/solid';

interface LowStockProduct {
  id: number;
  name: string;
  sku: string;
  stockQuantity: number;
  reorderLevel: number;
}

interface LowStockAlertProps {
  products: LowStockProduct[];
}

function LowStockAlert({ products }: LowStockAlertProps) {
  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-6 w-6 text-yellow-400" />
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">Low Stock Alert</h3>
          <div className="mt-2 text-sm text-yellow-700">
            <p className="mb-2">
              {products.length} product{products.length !== 1 ? 's' : ''} running low on stock:
            </p>
            <ul className="list-disc list-inside space-y-1">
              {products.slice(0, 5).map((product) => (
                <li key={product.id}>
                  <span className="font-medium">{product.name}</span>
                  <span className="text-xs ml-2">
                    ({product.stockQuantity} units left)
                  </span>
                </li>
              ))}
            </ul>
            {products.length > 5 && (
              <p className="mt-2 text-xs">
                ...and {products.length - 5} more product{products.length - 5 !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LowStockAlert;
