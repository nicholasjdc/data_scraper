import axios from 'axios';
import type {
  MultipleSeriesResponse,
  SearchResponse,
  SeriesResponse,
  SourcesResponse,
  DataSource,
  CensusQueryRequest,
  CensusQueryResponse,
  CensusDatasetsResponse,
  CensusVariablesResponse,
  CensusGeographiesResponse,
  FetchRecord,
  AIAnalysisRequest,
  AIAnalysisResponse,
} from '../types/api';

export interface ValidationResponse {
  is_valid: boolean;
  error_message: string | null;
  source: string;
  input: string;
}

export interface SuggestionItem {
  symbol: string;
  type: string;
}

export interface SuggestionsResponse {
  query: string;
  source: string;
  suggestions: SuggestionItem[];
  count: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export interface FetchCommonIndicatorsParams {
  start_date?: string;
  end_date?: string;
}

export interface SearchParams {
  q: string;
  source?: DataSource;
  limit?: number;
  order_by?: string;
  sort_order?: string;
}

export interface FetchSeriesParams {
  source?: DataSource;
  start_date?: string;
  end_date?: string;
  limit?: number;
  frequency?: string;
  aggregation_method?: string;
  units?: string;
}

export async function fetchCommonIndicators(
  params?: FetchCommonIndicatorsParams
): Promise<MultipleSeriesResponse> {
  try {
    const response = await apiClient.get<MultipleSeriesResponse>('/api/v1/indicators/common', { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch indicators');
    }
    throw error;
  }
}

export async function fetchSources(): Promise<SourcesResponse> {
  try {
    const response = await apiClient.get<SourcesResponse>('/api/v1/sources');
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch sources');
    }
    throw error;
  }
}

export async function fetchSearchResults(params: SearchParams): Promise<SearchResponse> {
  try {
    const response = await apiClient.get<SearchResponse>('/api/v1/search', { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to search series');
    }
    throw error;
  }
}

export async function fetchSeries(
  series_id: string,
  params?: FetchSeriesParams
): Promise<SeriesResponse> {
  try {
    const response = await apiClient.get<SeriesResponse>(`/api/v1/series/${series_id}`, { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch series');
    }
    throw error;
  }
}

export async function validateInput(
  source: DataSource,
  inputValue: string
): Promise<ValidationResponse> {
  try {
    const response = await apiClient.get<ValidationResponse>(`/api/v1/validate/${source}`, {
      params: { input_value: inputValue },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to validate input');
    }
    throw error;
  }
}

export async function getSuggestions(
  source: DataSource,
  query: string,
  category?: string,
  limit?: number
): Promise<SuggestionsResponse> {
  try {
    const params: Record<string, unknown> = { q: query };
    if (category) params.category = category;
    if (limit) params.limit = limit;
    const response = await apiClient.get<SuggestionsResponse>(`/api/v1/suggestions/${source}`, { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to get suggestions');
    }
    throw error;
  }
}

// Census
export async function fetchCensusDatasets(
  datasetType?: 'year_based' | 'timeseries'
): Promise<CensusDatasetsResponse> {
  try {
    const params: Record<string, unknown> = {};
    if (datasetType) params.dataset_type = datasetType;
    const response = await apiClient.get<CensusDatasetsResponse>('/api/v1/census/datasets', { params });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch Census datasets');
    }
    throw error;
  }
}

export async function fetchCensusVariables(
  dataset: string,
  year?: number
): Promise<CensusVariablesResponse> {
  try {
    const params: Record<string, unknown> = {};
    if (year) params.year = year;
    const response = await apiClient.get<CensusVariablesResponse>(
      `/api/v1/census/datasets/${dataset}/variables`,
      { params }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch Census variables');
    }
    throw error;
  }
}

export async function fetchCensusGeographies(dataset: string): Promise<CensusGeographiesResponse> {
  try {
    const response = await apiClient.get<CensusGeographiesResponse>(
      `/api/v1/census/datasets/${dataset}/geographies`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch Census geographies');
    }
    throw error;
  }
}

export async function executeCensusQuery(query: CensusQueryRequest): Promise<CensusQueryResponse> {
  try {
    const response = await apiClient.post<CensusQueryResponse>('/api/v1/census/query', query);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to execute Census query');
    }
    throw error;
  }
}

// Provenance
export async function fetchProvenance(fetchId: string): Promise<FetchRecord> {
  try {
    const response = await apiClient.get<FetchRecord>(`/api/v1/provenance/${fetchId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch provenance record');
    }
    throw error;
  }
}

// AI analysis
export async function analyzeWithAI(request: AIAnalysisRequest): Promise<AIAnalysisResponse> {
  try {
    const response = await apiClient.post<AIAnalysisResponse>('/api/v1/ai/analyze', request);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message || 'AI analysis failed');
    }
    throw error;
  }
}
