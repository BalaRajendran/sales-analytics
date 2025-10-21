/**
 * DateRangeSelector Component
 *
 * Dropdown to select date range for analytics.
 */

import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { ChevronDownIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { DATE_RANGES, type DateRangeKey } from '../../utils/dateHelpers';

interface DateRangeSelectorProps {
  selectedRange: DateRangeKey;
  onRangeChange: (range: DateRangeKey) => void;
}

function DateRangeSelector({ selectedRange, onRangeChange }: DateRangeSelectorProps) {
  return (
    <Menu as="div" className="relative inline-block text-left">
      <Menu.Button className="inline-flex items-center justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
        <CalendarIcon className="h-5 w-5 mr-2 text-gray-400" />
        {DATE_RANGES[selectedRange].label}
        <ChevronDownIcon className="ml-2 -mr-1 h-5 w-5 text-gray-400" />
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="py-1">
            {(Object.keys(DATE_RANGES) as DateRangeKey[]).map((key) => (
              <Menu.Item key={key}>
                {({ active }) => (
                  <button
                    onClick={() => onRangeChange(key)}
                    className={`${
                      active ? 'bg-gray-50 text-gray-900' : 'text-gray-700'
                    } ${
                      selectedRange === key ? 'font-semibold bg-primary-50 text-primary-700' : ''
                    } block w-full text-left px-4 py-2 text-sm`}
                  >
                    {DATE_RANGES[key].label}
                  </button>
                )}
              </Menu.Item>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
}

export default DateRangeSelector;
