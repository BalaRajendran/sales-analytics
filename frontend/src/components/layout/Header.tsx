/**
 * Header Component
 *
 * Top header with user info and actions.
 */

import { useState } from 'react';
import { Menu } from '@headlessui/react';
import {
  BellIcon,
  UserCircleIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

function Header() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      {/* Search Bar */}
      <div className="flex-1 max-w-lg">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search products, customers, orders..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <button className="relative p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50">
          <BellIcon className="h-6 w-6" />
          <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
        </button>

        {/* User Menu */}
        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50">
            <UserCircleIcon className="h-8 w-8 text-gray-400" />
            <div className="text-left">
              <div className="text-sm font-medium text-gray-900">Admin User</div>
              <div className="text-xs text-gray-500">admin@shopx.com</div>
            </div>
          </Menu.Button>

          <Menu.Items className="absolute right-0 mt-2 w-48 origin-top-right bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
            <div className="py-1">
              <Menu.Item>
                {({ active }) => (
                  <a
                    href="/profile"
                    className={`${
                      active ? 'bg-gray-50' : ''
                    } block px-4 py-2 text-sm text-gray-700`}
                  >
                    Your Profile
                  </a>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <a
                    href="/settings"
                    className={`${
                      active ? 'bg-gray-50' : ''
                    } block px-4 py-2 text-sm text-gray-700`}
                  >
                    Settings
                  </a>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    className={`${
                      active ? 'bg-gray-50' : ''
                    } block w-full text-left px-4 py-2 text-sm text-gray-700`}
                  >
                    Sign out
                  </button>
                )}
              </Menu.Item>
            </div>
          </Menu.Items>
        </Menu>
      </div>
    </header>
  );
}

export default Header;
