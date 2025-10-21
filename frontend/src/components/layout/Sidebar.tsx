/**
 * Sidebar Component
 *
 * Navigation sidebar with menu items.
 */

import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  ShoppingBagIcon,
  UserGroupIcon,
  UserCircleIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
  { name: 'Products', path: '/products', icon: ShoppingBagIcon },
  { name: 'Customers', path: '/customers', icon: UserGroupIcon },
  { name: 'Sales Reps', path: '/sales-reps', icon: UserCircleIcon },
  { name: 'Analytics', path: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', path: '/settings', icon: Cog6ToothIcon },
];

function Sidebar() {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-primary-600">ShopX Analytics</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon className="h-5 w-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          v1.0.0 • © 2025 ShopX
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
