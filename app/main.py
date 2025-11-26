from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.services.fred_service import get_fred_service
from app.services.alphavantage_service import get_alphavantage_service
from app.services.yfinance_service import get_yfinance_service
from app.services.worldbank_service import get_worldbank_service
from app.services.census_service import get_census_service
from app.models import (
    SeriesResponse,
    SeriesInfoResponse,
    SearchResponse,
    MultipleSeriesResponse,
    SourcesResponse,
    DataSourceInfo
)

app = FastAPI(
    title="Economic Data API",
    description="API for accessing economic data from multiple sources (FRED, Alpha Vantage, Yahoo Finance, World Bank, U.S. Census Bureau)",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Economic Data API",
        "endpoints": {
            "health": "/health",
            "sources": "/api/v1/sources",
            "series": "/api/v1/series/{series_id}",
            "series_info": "/api/v1/series/{series_id}/info",
            "search": "/api/v1/search",
            "multiple_series": "/api/v1/series/multiple",
            "common_indicators": "/api/v1/indicators/common"
        }
    }


def get_service(source: str):
    """Get the appropriate service based on source parameter."""
    source = source.lower() if source else "fred"
    
    if source == "fred":
        return get_fred_service()
    elif source == "alphavantage":
        return get_alphavantage_service()
    elif source == "yfinance":
        return get_yfinance_service()
    elif source == "worldbank":
        return get_worldbank_service()
    elif source == "census":
        return get_census_service()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown data source: {source}. Available sources: fred, alphavantage, yfinance, worldbank, census"
        )


@app.get("/api/v1/sources", response_model=SourcesResponse)
async def get_sources():
    """Get list of available data sources."""
    sources = [
        DataSourceInfo(
            id="fred",
            name="FRED (Federal Reserve Economic Data)",
            description="U.S. economic data from the Federal Reserve",
            requires_api_key=True,
            supports_search=True
        ),
        DataSourceInfo(
            id="alphavantage",
            name="Alpha Vantage",
            description="Stock, forex, and cryptocurrency data",
            requires_api_key=True,
            supports_search=False
        ),
        DataSourceInfo(
            id="yfinance",
            name="Yahoo Finance",
            description="Stock, ETF, and index data",
            requires_api_key=False,
            supports_search=False
        ),
        DataSourceInfo(
            id="worldbank",
            name="World Bank",
            description="Global economic indicators",
            requires_api_key=False,
            supports_search=True
        ),
        DataSourceInfo(
            id="census",
            name="U.S. Census Bureau",
            description="U.S. economic and demographic data",
            requires_api_key=False,
            supports_search=False
        )
    ]
    
    return SourcesResponse(sources=sources)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/v1/series/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: str,
    source: str = Query("fred", description="Data source (fred, alphavantage, yfinance, worldbank, census)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(None, description="Maximum number of observations"),
    frequency: Optional[str] = Query(None, description="Data frequency (d, w, m, q, a)"),
    aggregation_method: Optional[str] = Query(None, description="Aggregation method (avg, sum, eop)"),
    units: Optional[str] = Query(None, description="Data units (lin, chg, pch, log, etc.)")
):
    """
    Get economic data series from specified source.
    
    Examples:
    - FRED: GDP, UNRATE, CPIAUCSL
    - Alpha Vantage: AAPL, MSFT (stocks), EUR/USD (forex)
    - Yahoo Finance: AAPL, MSFT, ^GSPC (S&P 500)
    - World Bank: NY.GDP.MKTP.CD (GDP), SP.POP.TOTL (Population)
    - Census: Various economic indicators
    """
    service = get_service(source)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail=f"Service {source} is not available. Please check API key configuration."
        )
    
    result = service.get_series(
        series_id=series_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        frequency=frequency,
        aggregation_method=aggregation_method,
        units=units
    )
    
    # Add source to response
    result["source"] = source.lower()
    return result


@app.get("/api/v1/series/{series_id}/info", response_model=SeriesInfoResponse)
async def get_series_info(series_id: str):
    """Get metadata about a FRED series."""
    fred_service = get_fred_service()
    return fred_service.get_series_info(series_id)


@app.get("/api/v1/search", response_model=SearchResponse)
async def search_series(
    q: str = Query(..., description="Search query"),
    source: str = Query("fred", description="Data source (fred, alphavantage, yfinance, worldbank, census)"),
    limit: int = Query(20, ge=1, le=1000, description="Maximum number of results"),
    order_by: Optional[str] = Query(None, description="Order by field (only supported by FRED)"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc or desc, only supported by FRED)")
):
    """
    Search for economic data series in specified source.
    
    Note: order_by and sort_order parameters are only fully supported by FRED.
    Other sources may ignore these parameters or apply client-side sorting.
    """
    service = get_service(source)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail=f"Service {source} is not available. Please check API key configuration."
        )
    
    return service.search_series(
        search_text=q,
        limit=limit,
        order_by=order_by,
        sort_order=sort_order
    )


# Census Bureau specific endpoints
@app.get("/api/v1/census/datasets")
async def get_census_datasets(
    dataset_type: Optional[str] = Query(None, description="Filter by type: 'year_based' or 'timeseries'")
):
    """Get available Census Bureau datasets."""
    census_service = get_census_service()
    datasets = census_service.get_datasets(dataset_type=dataset_type)
    return {"datasets": datasets}


@app.get("/api/v1/census/datasets/{dataset}/variables")
async def get_census_variables(
    dataset: str,
    year: Optional[int] = Query(None, description="Year for year-based datasets")
):
    """Get available variables for a Census dataset."""
    try:
        census_service = get_census_service()
        variables = census_service.get_variables(dataset, year=year)
        if not variables:
            # Return a helpful message if no variables found
            return {
                "variables": [],
                "message": f"No variables could be automatically discovered for dataset '{dataset}'. You may need to consult the Census Bureau documentation or try entering variable names manually."
            }
        return {"variables": variables}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching variables: {str(e)}"
        )


@app.get("/api/v1/census/datasets/{dataset}/geographies")
async def get_census_geographies(dataset: str):
    """Get available geography types for a Census dataset."""
    census_service = get_census_service()
    geographies = census_service.get_geographies(dataset)
    return {"geographies": geographies}


@app.post("/api/v1/census/query")
async def execute_census_query(query: dict):
    """
    Execute a Census Bureau API query.
    
    Expected query format:
    {
        "dataset": "pep/population" or "timeseries/eits/mid",
        "variables": ["POP", "BIRTHS"],
        "geography": "us:1" or "state:*",
        "year": 2019 (for year-based datasets),
        "time_range": {"start": "2020-01-01", "end": "2024-01-01"} (for timeseries)
    }
    """
    census_service = get_census_service()
    
    dataset = query.get("dataset")
    variables = query.get("variables", [])
    geography = query.get("geography", "us:1")
    year = query.get("year")
    time_range = query.get("time_range")
    
    if not dataset:
        raise HTTPException(status_code=400, detail="Dataset is required")
    
    if not variables or not isinstance(variables, list):
        raise HTTPException(status_code=400, detail="Variables must be a non-empty list")
    
    try:
        result = census_service.execute_query(
            dataset=dataset,
            variables=variables,
            geography=geography,
            year=year,
            time_range=time_range
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing Census query: {str(e)}"
        )


@app.get("/api/v1/validate/{source}")
async def validate_input(
    source: str,
    input_value: str = Query(..., description="Input value to validate (symbol, ticker, variable name)")
):
    """
    Validate input format for specified source.
    
    Returns validation result with error message if invalid.
    """
    service = get_service(source)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail=f"Service {source} is not available. Please check API key configuration."
        )
    
    # Call appropriate validation method based on source
    if source == "yfinance":
        is_valid, error_message = service.validate_symbol(input_value)
    elif source == "alphavantage":
        is_valid, error_message = service.validate_symbol(input_value)
    elif source == "census":
        is_valid, error_message = service.validate_variable(input_value)
    else:
        # For sources without validation, return true
        is_valid, error_message = True, None
    
    return {
        "is_valid": is_valid,
        "error_message": error_message,
        "source": source,
        "input": input_value
    }


@app.get("/api/v1/suggestions/{source}")
async def get_suggestions(
    source: str,
    q: str = Query("", description="Search query for suggestions"),
    category: Optional[str] = Query(None, description="Category filter (for alphavantage: stocks, forex, crypto)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of suggestions")
):
    """
    Get autocomplete suggestions for specified source.
    
    Returns list of suggestions matching the query.
    """
    service = get_service(source)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail=f"Service {source} is not available. Please check API key configuration."
        )
    
    try:
        if source == "yfinance":
            suggestions = service.get_suggestions(q, limit=limit)
            # Convert to list of dicts with symbol
            results = [{"symbol": s, "type": "ticker"} for s in suggestions]
        elif source == "alphavantage":
            suggestions = service.get_suggestions(q, category=category, limit=limit)
            # Convert list of tuples to list of dicts
            results = [{"symbol": s[0], "type": s[1]} for s in suggestions]
        elif source == "census":
            suggestions = service.get_suggestions(q, category=category, limit=limit)
            # Convert to list of dicts with variable name
            results = [{"symbol": s, "type": "variable"} for s in suggestions]
        else:
            results = []
        
        return {
            "query": q,
            "source": source,
            "suggestions": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting suggestions: {str(e)}"
        )


@app.post("/api/v1/series/multiple", response_model=MultipleSeriesResponse)
async def get_multiple_series(
    series_ids: List[str],
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get multiple economic data series at once.
    
    Provide series IDs as a JSON array in the request body.
    """
    if not series_ids:
        raise HTTPException(status_code=400, detail="series_ids cannot be empty")
    
    fred_service = get_fred_service()
    return fred_service.get_multiple_series(
        series_ids=series_ids,
        start_date=start_date,
        end_date=end_date
    )


@app.get("/api/v1/indicators/common")
async def get_common_indicators(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get common economic indicators in one call.
    
    Returns: GDP, Unemployment Rate, CPI, Federal Funds Rate, S&P 500, 10-Year Treasury
    """
    common_series = {
        "GDP": "Gross Domestic Product",
        "UNRATE": "Unemployment Rate",
        "CPIAUCSL": "Consumer Price Index",
        "FEDFUNDS": "Federal Funds Rate",
        "SP500": "S&P 500 Index",
        "DGS10": "10-Year Treasury Rate"
    }
    
    fred_service = get_fred_service()
    return fred_service.get_multiple_series(
        series_ids=list(common_series.keys()),
        start_date=start_date,
        end_date=end_date
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

