/**
 * Default configurations and presets for graph module
 * Supports extensibility for future chart types
 */

import type { LineChartConfig, BarChartConfig, AreaChartConfig, ChartType } from './graphTypes';

/**
 * Default color palette for charts
 */
export const DEFAULT_COLORS = [
  '#8884d8', // Blue
  '#82ca9d', // Green
  '#ffc658', // Yellow
  '#ff7300', // Orange
  '#0088fe', // Light Blue
  '#00c49f', // Teal
  '#ffbb28', // Gold
  '#ff8042', // Coral
];

/**
 * Default margin configuration
 */
export const DEFAULT_MARGIN = {
  top: 20,
  right: 30,
  left: 20,
  bottom: 20,
};

/**
 * Default line chart configuration
 */
export const DEFAULT_LINE_CHART_CONFIG: LineChartConfig = {
  width: '100%',
  height: 400,
  margin: DEFAULT_MARGIN,
  colors: DEFAULT_COLORS,
  showLegend: true,
  showGrid: true,
  responsive: true,
  strokeWidth: 2,
  dot: false,
  activeDot: { r: 6 },
  connectNulls: false,
};

/**
 * Default bar chart configuration (for future use)
 */
export const DEFAULT_BAR_CHART_CONFIG: BarChartConfig = {
  width: '100%',
  height: 400,
  margin: DEFAULT_MARGIN,
  colors: DEFAULT_COLORS,
  showLegend: true,
  showGrid: true,
  responsive: true,
  barSize: 20,
  barCategoryGap: '10%',
  barGap: 4,
};

/**
 * Default area chart configuration (for future use)
 */
export const DEFAULT_AREA_CHART_CONFIG: AreaChartConfig = {
  width: '100%',
  height: 400,
  margin: DEFAULT_MARGIN,
  colors: DEFAULT_COLORS,
  showLegend: true,
  showGrid: true,
  responsive: true,
  strokeWidth: 2,
  fillOpacity: 0.6,
  connectNulls: false,
};

/**
 * Get default configuration for a chart type
 */
export function getDefaultConfig(chartType: ChartType = 'line'): LineChartConfig | BarChartConfig | AreaChartConfig {
  switch (chartType) {
    case 'line':
      return DEFAULT_LINE_CHART_CONFIG;
    case 'bar':
      return DEFAULT_BAR_CHART_CONFIG;
    case 'area':
      return DEFAULT_AREA_CHART_CONFIG;
    default:
      return DEFAULT_LINE_CHART_CONFIG;
  }
}

/**
 * Merge user config with defaults
 */
export function mergeConfig<T extends LineChartConfig | BarChartConfig | AreaChartConfig>(
  defaultConfig: T,
  userConfig?: Partial<T>
): T {
  if (!userConfig) {
    return defaultConfig;
  }

  return {
    ...defaultConfig,
    ...userConfig,
    margin: {
      ...defaultConfig.margin,
      ...userConfig.margin,
    },
  };
}

/**
 * Responsive breakpoints
 */
export const BREAKPOINTS = {
  mobile: 640,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
};

/**
 * Get responsive width based on container
 */
export function getResponsiveWidth(containerWidth?: number): number | string {
  if (!containerWidth) {
    return '100%';
  }
  return Math.min(containerWidth - 40, 1200);
}





