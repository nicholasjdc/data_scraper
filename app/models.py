from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class SeriesDataPoint(BaseModel):
    """Single data point in a time series."""
    date: str
    value: Optional[float] = None


# Data source types
DataSource = Literal["fred", "alphavantage", "yfinance", "worldbank", "census"]

class SeriesResponse(BaseModel):
    """Response model for a single data series."""
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
    source: Optional[str] = Field(default="fred", description="Data source identifier")


class SeriesInfoResponse(BaseModel):
    """Response model for series metadata."""
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
    """Single search result."""
    series_id: str
    title: str
    units: str
    frequency: str
    seasonal_adjustment: str
    popularity: int


class SearchResponse(BaseModel):
    """Response model for series search."""
    query: str
    results: List[SearchResult]
    count: int


class MultipleSeriesResponse(BaseModel):
    """Response model for multiple series."""
    series: dict
    errors: List[dict]
    successful: int
    failed: int
    source: Optional[str] = Field(default="fred", description="Data source identifier")

class DataSourceInfo(BaseModel):
    """Information about a data source."""
    id: str
    name: str
    description: str
    requires_api_key: bool
    supports_search: bool

class SourcesResponse(BaseModel):
    """Response model for available data sources."""
    sources: List[DataSourceInfo]


# Census Bureau models
class CensusDatasetInfo(BaseModel):
    """Information about a Census dataset."""
    id: str
    name: str
    years: Optional[List[int]] = None  # For year-based datasets


class CensusVariableInfo(BaseModel):
    """Information about a Census variable."""
    id: str
    name: str
    description: str = ""


class CensusGeographyInfo(BaseModel):
    """Information about a Census geography type."""
    id: str
    name: str
    level: str  # national, state, county, tract, etc.


class CensusQueryRequest(BaseModel):
    """Request model for Census query."""
    dataset: str
    variables: List[str]
    geography: str = "us:1"
    year: Optional[int] = None  # For year-based datasets
    time_range: Optional[Dict[str, str]] = None  # For timeseries datasets: {"start": "2020-01-01", "end": "2024-01-01"}


class CensusQueryResponse(BaseModel):
    """Response model for Census query."""
    dataset: str
    year: Optional[int] = None
    geography: str
    variables: List[str]
    headers: List[str]
    data: List[Dict[str, Any]]
    count: int

