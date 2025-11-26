/**
 * TimeSeriesGraph Component
 * Main graph component for rendering time series data
 * Designed to be extensible for future chart types
 */

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { TimeSeriesGraphProps } from './graphTypes';
import { getDefaultConfig, mergeConfig, DEFAULT_COLORS } from './graphConfig';
import { formatDate, formatValue } from './dataTransform';
import type { LineChartConfig } from './graphTypes';

/**
 * Custom tooltip component for time series
 */
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          backgroundColor: 'white',
          border: '1px solid #ccc',
          borderRadius: '4px',
          padding: '10px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <p style={{ marginBottom: '5px', fontWeight: 'bold' }}>
          {formatDate(label, 'long')}
        </p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color, margin: '2px 0' }}>
            {`${entry.name}: ${formatValue(entry.value, entry.payload?.metadata?.units)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

/**
 * Format Y-axis tick based on value
 */
const formatYAxisTick = (value: number, metadata?: { units?: string }) => {
  return formatValue(value, metadata?.units);
};

/**
 * Format X-axis tick (date)
 */
const formatXAxisTick = (tickItem: string) => {
  const date = new Date(tickItem);
  return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
};

/**
 * TimeSeriesGraph Component
 * Renders time series data as a line chart (extensible for other chart types)
 */
const TimeSeriesGraph: React.FC<TimeSeriesGraphProps> = ({
  datasets,
  chartType = 'line',
  config: userConfig,
}) => {
  // Get default config and merge with user config
  const defaultConfig = getDefaultConfig(chartType) as LineChartConfig;
  const config = mergeConfig(defaultConfig, userConfig) as LineChartConfig;

  // Transform data for Recharts format
  const chartData = useMemo(() => {
    if (datasets.length === 0) {
      return [];
    }

    // Get all unique dates across all datasets
    const allDates = new Set<string>();
    datasets.forEach((dataset) => {
      dataset.data.forEach((point) => {
        const dateStr = point.date instanceof Date ? point.date.toISOString() : point.date;
        allDates.add(dateStr);
      });
    });

    // Create a map of date -> values for each dataset
    const dataMap = new Map<string, Record<string, number | null>>();
    
    datasets.forEach((dataset) => {
      dataset.data.forEach((point) => {
        const dateStr = point.date instanceof Date ? point.date.toISOString() : point.date;
        if (!dataMap.has(dateStr)) {
          dataMap.set(dateStr, { date: dateStr });
        }
        dataMap.get(dateStr)![dataset.id] = point.value;
        // Store metadata for tooltip
        if (dataset.metadata) {
          dataMap.get(dateStr)![`${dataset.id}_metadata`] = dataset.metadata;
        }
      });
    });

    // Convert to array and sort by date
    return Array.from(dataMap.values()).sort((a, b) => {
      return new Date(a.date as string).getTime() - new Date(b.date as string).getTime();
    });
  }, [datasets]);

  // For now, only support line charts (extensible for future chart types)
  if (chartType !== 'line') {
    console.warn(`Chart type "${chartType}" not yet implemented. Falling back to line chart.`);
  }

  const width = config.width || '100%';
  const height = config.height || 400;

  return (
    <ResponsiveContainer width={width} height={height}>
      <LineChart
        data={chartData}
        margin={config.margin}
      >
        {config.showGrid && <CartesianGrid strokeDasharray="3 3" />}
        <XAxis
          dataKey="date"
          tickFormatter={formatXAxisTick}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis tickFormatter={(value) => formatYAxisTick(value, datasets[0]?.metadata)} />
        <Tooltip content={<CustomTooltip />} />
        {config.showLegend && <Legend />}
        {datasets.map((dataset, index) => {
          const color = config.colors?.[index % (config.colors?.length || DEFAULT_COLORS.length)] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
          return (
            <Line
              key={dataset.id}
              type="monotone"
              dataKey={dataset.id}
              name={dataset.label}
              stroke={color}
              strokeWidth={config.strokeWidth}
              dot={config.dot}
              activeDot={config.activeDot}
              connectNulls={config.connectNulls}
            />
          );
        })}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TimeSeriesGraph;





