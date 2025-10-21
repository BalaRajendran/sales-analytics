/**
 * Products Page
 *
 * Product management and insights.
 */

import { useState } from 'react';
import { useQuery } from '@apollo/client';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

import { GET_ALL_PRODUCTS } from '../graphql/queries';
import ProductsTable from '../components/products/ProductsTable';
import LowStockAlert from '../components/products/LowStockAlert';

function Products() {
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all products
  const { data: productsData, loading: productsLoading } = useQuery(GET_ALL_PRODUCTS, {
    variables: { limit: 100, offset: 0 }
  });

  // Access products through edges
  const products = productsData?.products?.edges || [];

  // Filter low stock products (stockQuantity < 10)
  const lowStockProducts = products.filter((product: any) => product.stockQuantity < 10);

  // Filter products based on search
  const filteredProducts = products.filter(
    (product: any) =>
      product.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Products</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage inventory and track product performance
            </p>
          </div>
          <button className="btn-primary flex items-center">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Product
          </button>
        </div>
      </div>

      {/* Low Stock Alert */}
      {!productsLoading && lowStockProducts.length > 0 && (
        <div className="mb-6">
          <LowStockAlert products={lowStockProducts} />
        </div>
      )}

      {/* Filters & Search */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          {/* Search Bar */}
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search products by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>

          {/* Filter Button */}
          <button className="btn-secondary ml-4 flex items-center">
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filters
          </button>
        </div>
      </div>

      {/* Products Table */}
      <ProductsTable products={filteredProducts} loading={productsLoading} />
    </div>
  );
}

export default Products;
