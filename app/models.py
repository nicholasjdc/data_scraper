from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class SeriesDataPoint(BaseModel):
    date: str
    value: Optional[float] = None


DataSource = Literal["fred", "alphavantage", "yfinance", "worldbank", "census", "edgar", "oecd", "ecb"]


class SeriesResponse(BaseModel):
    series_id: str
    title: str
    units: str
    frequency: str
    seasonal_adjustment: str
    last_updated: str
    observation_start: str
    observation_end: str
    data: List[SeriesDataPoint]
    data_points: int
    source: Optional[str] = Field(default="fred")
    fetch_id: Optional[str] = None
    fetched_at: Optional[str] = None


class SeriesInfoResponse(BaseModel):
    series_id: str
    title: str
    observation_start: str
    observation_end: str
    frequency: str
    frequency_short: str
    units: str
    units_short: str
    seasonal_adjustment: str
    seasonal_adjustment_short: str
    last_updated: str
    popularity: int
    notes: str


class SearchResult(BaseModel):
    series_id: str
    title: str
    units: str
    frequency: str
    seasonal_adjustment: str
    popularity: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    count: int


class SeriesInfoWithProvenance(BaseModel):
    title: str
    units: str
    frequency: str
    data: List[SeriesDataPoint]
    data_points: int
    fetch_id: Optional[str] = None
    fetched_at: Optional[str] = None


class MultipleSeriesResponse(BaseModel):
    series: Dict[str, SeriesInfoWithProvenance]
    errors: List[dict]
    successful: int
    failed: int
    source: Optional[str] = Field(default="fred")


class DataSourceInfo(BaseModel):
    id: str
    name: str
    description: str
    requires_api_key: bool
    supports_search: bool


class SourcesResponse(BaseModel):
    sources: List[DataSourceInfo]


# Census Bureau models
class CensusDatasetInfo(BaseModel):
    id: str
    name: str
    years: Optional[List[int]] = None


class CensusVariableInfo(BaseModel):
    id: str
    name: str
    description: str = ""


class CensusGeographyInfo(BaseModel):
    id: str
    name: str
    level: str


class CensusQueryRequest(BaseModel):
    dataset: str
    variables: List[str]
    geography: str = "us:1"
    year: Optional[int] = None
    time_range: Optional[Dict[str, str]] = None


class CensusQueryResponse(BaseModel):
    dataset: str
    year: Optional[int] = None
    geography: str
    variables: List[str]
    headers: List[str]
    data: List[Dict[str, Any]]
    count: int
    fetch_id: Optional[str] = None
    fetched_at: Optional[str] = None


# Provenance
class FetchRecord(BaseModel):
    fetch_id: str
    source: str
    series_id: str
    request_params: Dict[str, Any]
    fetched_at: str
    response_sha256: str
    latency_ms: Optional[int] = None


# AI analysis
class AIAnalysisClaim(BaseModel):
    text: str
    fetch_id: str
    series_id: str
    date: str
    value: float
    verified: bool = False
    verification_note: str = ""


class AIAnalysisRequest(BaseModel):
    fetch_ids: List[str]
    question: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    analysis_id: str
    model_id: str
    summary: str
    claims: List[AIAnalysisClaim]
    data_gaps: List[str] = []
    input_fetch_ids: List[str]
    verified: bool
