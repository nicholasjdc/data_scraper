/**
 * Data transformation utilities for time series data
 * Pure functions that work with any time series dataset
 */

import type { TimeSeriesDataPoint, TimeSeriesDataset } from './graphTypes';

/**
 * Parse a date string or Date object into a Date
 */
export function parseDate(date: string | Date): Date {
  if (date instanceof Date) {
    return date;
  }
  return new Date(date);
}

/**
 * Normalize time series data from various input formats
 * Converts API response format to standardized TimeSeriesDataPoint format
 */
export function normalizeTimeSeriesData(
  data: Array<{ date: string; value: number | null }>
): TimeSeriesDataPoint[] {
  return data.map((point) => ({
    date: point.date,
    value: point.value,
  }));
}

/**
 * Filter data by date range
 */
export function filterDataByDateRange(
  data: TimeSeriesDataPoint[],
  startDate?: string | Date,
  endDate?: string | Date
): TimeSeriesDataPoint[] {
  if (!startDate && !endDate) {
    return data;
  }

  const start = startDate ? parseDate(startDate).getTime() : -Infinity;
  const end = endDate ? parseDate(endDate).getTime() : Infinity;

  return data.filter((point) => {
    const pointDate = parseDate(point.date).getTime();
    return pointDate >= start && pointDate <= end;
  });
}

/**
 * Handle missing values in time series data
 * Options: 'remove', 'zero', 'interpolate'
 */
export function handleMissingValues(
  data: TimeSeriesDataPoint[],
  strategy: 'remove' | 'zero' | 'interpolate' = 'remove'
): TimeSeriesDataPoint[] {
  switch (strategy) {
    case 'remove':
      return data.filter((point) => point.value !== null && !isNaN(point.value as number));

    case 'zero':
      return data.map((point) => ({
        ...point,
        value: point.value === null || isNaN(point.value as number) ? 0 : point.value,
      }));

    case 'interpolate':
      return interpolateMissingValues(data);

    default:
      return data;
  }
}

/**
 * Interpolate missing values using linear interpolation
 */
function interpolateMissingValues(data: TimeSeriesDataPoint[]): TimeSeriesDataPoint[] {
  const result: TimeSeriesDataPoint[] = [];
  let lastValidValue: number | null = null;
  let lastValidIndex = -1;

  for (let i = 0; i < data.length; i++) {
    const point = data[i];
    const value = point.value;

    if (value !== null && !isNaN(value)) {
      // Fill any gaps between last valid value and current
      if (lastValidIndex >= 0 && lastValidIndex < i - 1 && lastValidValue !== null) {
        const gap = i - lastValidIndex;
        for (let j = lastValidIndex + 1; j < i; j++) {
          const ratio = (j - lastValidIndex) / gap;
          const interpolatedValue = lastValidValue + (value - lastValidValue) * ratio;
          result.push({
            ...data[j],
            value: interpolatedValue,
          });
        }
      }
      result.push(point);
      lastValidValue = value;
      lastValidIndex = i;
    } else {
      result.push(point);
    }
  }

  return result;
}

/**
 * Sort data points by date
 */
export function sortDataByDate(data: TimeSeriesDataPoint[]): TimeSeriesDataPoint[] {
  return [...data].sort((a, b) => {
    const dateA = parseDate(a.date).getTime();
    const dateB = parseDate(b.date).getTime();
    return dateA - dateB;
  });
}

/**
 * Format a date for display
 */
export function formatDate(date: string | Date, format: 'short' | 'long' = 'short'): string {
  const d = parseDate(date);
  if (format === 'long') {
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format a value for display based on units
 */
export function formatValue(value: number | null, units?: string): string {
  if (value === null || isNaN(value)) {
    return 'N/A';
  }

  // Format based on units
  if (units?.toLowerCase().includes('percent') || units?.includes('%')) {
    return `${value.toFixed(2)}%`;
  }

  if (units?.toLowerCase().includes('index')) {
    return value.toFixed(2);
  }

  // Default formatting for large numbers
  if (Math.abs(value) >= 1e9) {
    return `${(value / 1e9).toFixed(2)}B`;
  }
  if (Math.abs(value) >= 1e6) {
    return `${(value / 1e6).toFixed(2)}M`;
  }
  if (Math.abs(value) >= 1e3) {
    return `${(value / 1e3).toFixed(2)}K`;
  }

  return value.toFixed(2);
}





