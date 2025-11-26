// Type definitions matching the FastAPI backend models

export type DataSource = "fred" | "alphavantage" | "yfinance" | "worldbank" | "census";

export interface SeriesDataPoint {
  date: string;
  value: number | null;
}

export interface SeriesResponse {
  series_id: string;
  title: string;
  units: string;
  frequency: string;
  seasonal_adjustment: string;
  last_updated: string;
  observation_start: string;
  observation_end: string;
  data: SeriesDataPoint[];
  data_points: number;
  source?: string;
}

export interface SeriesInfo {
  title: string;
  units: string;
  frequency: string;
  data: SeriesDataPoint[];
  data_points: number;
}

export interface MultipleSeriesResponse {
  series: Record<string, SeriesInfo>;
  errors: Array<{
    series_id: string;
    error: string;
  }>;
  successful: number;
  failed: number;
}

export interface SearchResult {
  series_id: string;
  title: string;
  units: string;
  frequency: string;
  seasonal_adjustment: string;
  popularity: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
  message?: string;
}

export interface DataSourceInfo {
  id: string;
  name: string;
  description: string;
  requires_api_key: boolean;
  supports_search: boolean;
}

export interface SourcesResponse {
  sources: DataSourceInfo[];
}

// Census Bureau types
export interface CensusDataset {
  id: string;
  name: string;
  years?: number[];
}

export interface CensusVariable {
  id: string;
  name: string;
  description: string;
}

export interface CensusGeography {
  id: string;
  name: string;
  level: string;
}

export interface CensusQueryRequest {
  dataset: string;
  variables: string[];
  geography: string;
  year?: number;
  time_range?: {
    start: string;
    end: string;
  };
}

export interface CensusQueryResponse {
  dataset: string;
  year?: number;
  geography: string;
  variables: string[];
  headers: string[];
  data: Record<string, any>[];
  count: number;
}

export interface CensusDatasetsResponse {
  datasets: CensusDataset[];
}

export interface CensusVariablesResponse {
  variables: CensusVariable[];
  message?: string;
}

export interface CensusGeographiesResponse {
  geographies: CensusGeography[];
}




