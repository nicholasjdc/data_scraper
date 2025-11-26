/**
 * Core type definitions for the graph module
 * Designed to be extensible for future chart types
 */

export type ChartType = 'line' | 'bar' | 'area' | 'scatter';

export interface TimeSeriesDataPoint {
  date: string | Date;
  value: number | null;
}

export interface TimeSeriesMetadata {
  units?: string;
  frequency?: string;
  seasonal_adjustment?: string;
  [key: string]: unknown;
}

export interface TimeSeriesDataset {
  id: string;
  label: string;
  data: TimeSeriesDataPoint[];
  metadata?: TimeSeriesMetadata;
}

/**
 * Base configuration for all chart types
 */
export interface BaseGraphConfig {
  width?: number | string;
  height?: number;
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  colors?: string[];
  showLegend?: boolean;
  showGrid?: boolean;
  responsive?: boolean;
}

/**
 * Line chart specific configuration
 */
export interface LineChartConfig extends BaseGraphConfig {
  strokeWidth?: number;
  dot?: boolean;
  activeDot?: boolean;
  connectNulls?: boolean;
}

/**
 * Bar chart specific configuration (for future use)
 */
export interface BarChartConfig extends BaseGraphConfig {
  barSize?: number;
  barCategoryGap?: string | number;
  barGap?: string | number;
}

/**
 * Area chart specific configuration (for future use)
 */
export interface AreaChartConfig extends BaseGraphConfig {
  strokeWidth?: number;
  fillOpacity?: number;
  connectNulls?: boolean;
}

/**
 * Union type for all chart configurations
 */
export type GraphConfig = LineChartConfig | BarChartConfig | AreaChartConfig;

/**
 * Props for the TimeSeriesGraph component
 */
export interface TimeSeriesGraphProps {
  datasets: TimeSeriesDataset[];
  chartType?: ChartType;
  config?: GraphConfig;
}





