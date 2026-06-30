export type DataSource = "fred" | "alphavantage" | "yfinance" | "worldbank" | "census" | "edgar" | "oecd" | "ecb";

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
  fetch_id?: string;
  fetched_at?: string;
}

export interface SeriesInfoWithProvenance {
  title: string;
  units: string;
  frequency: string;
  data: SeriesDataPoint[];
  data_points: number;
  fetch_id?: string;
  fetched_at?: string;
}

export interface MultipleSeriesResponse {
  series: Record<string, SeriesInfoWithProvenance>;
  errors: Array<{ series_id: string; error: string }>;
  successful: number;
  failed: number;
  source?: string;
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
  time_range?: { start: string; end: string };
}

export interface CensusQueryResponse {
  dataset: string;
  year?: number;
  geography: string;
  variables: string[];
  headers: string[];
  data: Record<string, any>[];
  count: number;
  fetch_id?: string;
  fetched_at?: string;
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

// Provenance
export interface FetchRecord {
  fetch_id: string;
  source: string;
  series_id: string;
  request_params: Record<string, unknown>;
  fetched_at: string;
  response_sha256: string;
  latency_ms?: number;
}

// AI analysis
export interface AIAnalysisClaim {
  text: string;
  fetch_id: string;
  series_id: string;
  date: string;
  value: number;
  verified: boolean;
  verification_note: string;
}

export interface AIAnalysisRequest {
  fetch_ids: string[];
  question?: string;
}

export interface AIAnalysisResponse {
  analysis_id: string;
  model_id: string;
  summary: string;
  claims: AIAnalysisClaim[];
  data_gaps: string[];
  input_fetch_ids: string[];
  verified: boolean;
}
