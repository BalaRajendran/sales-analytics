/**
 * Customers Page
 *
 * Customer analytics and management.
 */

import { useState } from 'react';
import { useQuery } from '@apollo/client';
import { GET_ALL_CUSTOMERS, GET_CUSTOMER_SEGMENTS } from '../graphql/queries';
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

import CustomersTable from '../components/customers/CustomersTable';
import CustomerSegmentsChart from '../components/customers/CustomerSegmentsChart';

function Customers() {
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all customers
  const { data: customersData, loading: customersLoading } = useQuery(GET_ALL_CUSTOMERS, {
    variables: { limit: 100, offset: 0 }
  });

  // Fetch customer segments
  const { data: segmentsData, loading: segmentsLoading } = useQuery(GET_CUSTOMER_SEGMENTS);

  // Access customers through edges
  const customers = customersData?.customers?.edges || [];
  const segments = segmentsData?.customerSegmentDistribution || [];

  // Filter customers based on search
  const filteredCustomers = customers.filter(
    (customer: any) =>
      customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate totals
  const totalCustomers = customers.length;
  const totalLTV = customers.reduce((sum: number, c: any) => sum + (parseFloat(c.totalLifetimeValue) || 0), 0);
  const avgLTV = totalCustomers > 0 ? totalLTV / totalCustomers : 0;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
            <p className="text-sm text-gray-600 mt-1">
              Customer insights and lifetime value analytics
            </p>
          </div>
          <button className="btn-primary flex items-center">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Customer
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="stat-card">
          <p className="stat-label">Total Customers</p>
          <p className="stat-value">{customersLoading ? '...' : totalCustomers.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Total Lifetime Value</p>
          <p className="stat-value">
            {customersLoading ? '...' : `$${(totalLTV / 1000).toFixed(0)}k`}
          </p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Avg Lifetime Value</p>
          <p className="stat-value">
            {customersLoading ? '...' : `$${avgLTV.toFixed(0)}`}
          </p>
        </div>
      </div>

      {/* Customer Segments Chart */}
      <div className="mb-6">
        <CustomerSegmentsChart segments={segments} loading={segmentsLoading} />
      </div>

      {/* Search Bar */}
      <div className="card mb-6">
        <div className="flex items-center">
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search customers by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Customers Table */}
      <CustomersTable customers={filteredCustomers} loading={customersLoading} />
    </div>
  );
}

export default Customers;
