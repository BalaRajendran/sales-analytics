/**
 * Main App Component
 *
 * Routes and layout for the Sales Analytics Dashboard.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Customers from './pages/Customers';
import SalesReps from './pages/SalesReps';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/customers" element={<Customers />} />
        <Route path="/sales-reps" element={<SalesReps />} />
        <Route
          path="/analytics"
          element={
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Advanced Analytics</h1>
              <p className="text-gray-600">Analytics coming soon...</p>
            </div>
          }
        />
        <Route
          path="/settings"
          element={
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>
              <p className="text-gray-600">Settings coming soon...</p>
            </div>
          }
        />
        <Route
          path="*"
          element={
            <div>
              <h1 className="text-2xl font-bold text-red-600 mb-2">404 - Not Found</h1>
              <p className="text-gray-600">The page you're looking for doesn't exist.</p>
            </div>
          }
        />
      </Routes>
    </Layout>
  );
}

export default App;
