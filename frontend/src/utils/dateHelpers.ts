/**
 * Date Helper Functions
 *
 * Utilities for working with dates and date ranges.
 */

import { subDays, startOfDay, endOfDay, format } from 'date-fns';

export interface DateRange {
  startDate: Date;
  endDate: Date;
}

export const DATE_RANGES = {
  '7d': { label: 'Last 7 Days', days: 7 },
  '30d': { label: 'Last 30 Days', days: 30 },
  '90d': { label: 'Last 90 Days', days: 90 },
  '1y': { label: 'Last Year', days: 365 },
} as const;

export type DateRangeKey = keyof typeof DATE_RANGES;

/**
 * Get date range for a given key
 */
export function getDateRange(rangeKey: DateRangeKey): DateRange {
  const endDate = endOfDay(new Date());
  const startDate = startOfDay(subDays(endDate, DATE_RANGES[rangeKey].days));

  return { startDate, endDate };
}

/**
 * Format date for GraphQL (ISO 8601)
 */
export function formatForGraphQL(date: Date): string {
  return date.toISOString();
}

/**
 * Format date for display
 */
export function formatForDisplay(date: Date | string, formatStr: string = 'MMM d, yyyy'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, formatStr);
}

/**
 * Format currency
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

/**
 * Format number with commas
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

/**
 * Format percentage
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Calculate percentage change
 */
export function calculatePercentageChange(current: number, previous: number): number {
  if (previous === 0) return 0;
  return ((current - previous) / previous) * 100;
}
