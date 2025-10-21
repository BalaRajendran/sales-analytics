/**
 * CustomersTable Component
 *
 * Table displaying all customers with segments and LTV.
 */

import { formatCurrency, formatNumber, formatForDisplay } from '../../utils/dateHelpers';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  city: string;
  state: string;
  country: string;
  segment: string;
  lifetimeValue: number;
  totalOrders: number;
  createdAt: string;
}

interface CustomersTableProps {
  customers: Customer[];
  loading?: boolean;
}

const segmentColors: Record<string, string> = {
  premium: 'badge-success',
  regular: 'badge-info',
  new: 'badge-warning',
  'at-risk': 'badge-danger',
  churned: 'badge-gray',
};

function CustomersTable({ customers, loading = false }: CustomersTableProps) {
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
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Segment
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Lifetime Value
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Orders
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Since
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {customers.map((customer) => (
              <tr key={customer.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                    <div className="text-sm text-gray-500">{customer.email}</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">
                    {customer.city}, {customer.state}
                  </div>
                  <div className="text-xs text-gray-500">{customer.country}</div>
                </td>
                <td className="px-6 py-4 text-center">
                  <span className={segmentColors[customer.segment] || 'badge-gray'}>
                    {customer.segment}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="text-sm font-semibold text-gray-900">
                    {formatCurrency(customer.lifetimeValue)}
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="text-sm text-gray-900">{formatNumber(customer.totalOrders)}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-600">
                    {formatForDisplay(customer.createdAt, 'MMM yyyy')}
                  </div>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-primary-600 hover:text-primary-900 text-sm font-medium mr-3">
                    View
                  </button>
                  <button className="text-primary-600 hover:text-primary-900 text-sm font-medium">
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {customers.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No customers found</p>
          <p className="text-sm">Try adjusting your search</p>
        </div>
      )}
    </div>
  );
}

export default CustomersTable;
