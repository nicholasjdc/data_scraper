import time
from typing import Optional, List

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.provenance import record_fetch, get_fetch_record
from app.service_router import get_service
from app.services.fred_service import get_fred_service
from app.services.census_service import get_census_service
from app.models import (
    SeriesResponse,
    SeriesInfoResponse,
    SearchResponse,
    MultipleSeriesResponse,
    SeriesInfoWithProvenance,
    SourcesResponse,
    DataSourceInfo,
    CensusQueryResponse,
    FetchRecord,
    AIAnalysisRequest,
    AIAnalysisResponse,
)

app = FastAPI(
    title="Economic Data API",
    description="Multi-source economic data with full provenance tracking and AI analysis.",
    version="3.0.0",
)

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


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root():
    return {
        "message": "Economic Data API",
        "version": "3.0.0",
        "endpoints": {
            "sources": "/api/v1/sources",
            "series": "/api/v1/series/{series_id}",
            "search": "/api/v1/search",
            "common_indicators": "/api/v1/indicators/common",
            "provenance": "/api/v1/provenance/{fetch_id}",
            "ai_analyze": "/api/v1/ai/analyze",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/v1/sources", response_model=SourcesResponse)
async def get_sources():
    sources = [
        DataSourceInfo(
            id="fred",
            name="FRED (Federal Reserve Economic Data)",
            description="U.S. economic data from the Federal Reserve",
            requires_api_key=True,
            supports_search=True,
        ),
        DataSourceInfo(
            id="alphavantage",
            name="Alpha Vantage",
            description="Stock, forex, and cryptocurrency data",
            requires_api_key=True,
            supports_search=False,
        ),
        DataSourceInfo(
            id="yfinance",
            name="Yahoo Finance",
            description="Stock, ETF, and index data",
            requires_api_key=False,
            supports_search=False,
        ),
        DataSourceInfo(
            id="worldbank",
            name="World Bank",
            description="Global economic indicators",
            requires_api_key=False,
            supports_search=True,
        ),
        DataSourceInfo(
            id="census",
            name="U.S. Census Bureau",
            description="U.S. economic and demographic data",
            requires_api_key=False,
            supports_search=False,
        ),
        DataSourceInfo(
            id="edgar",
            name="SEC EDGAR",
            description="U.S. company fundamentals from XBRL filings (format: TICKER:CONCEPT)",
            requires_api_key=False,
            supports_search=True,
        ),
        DataSourceInfo(
            id="oecd",
            name="OECD",
            description="International macro data — GDP, unemployment, CPI, rates (format: DATASET:KEY)",
            requires_api_key=False,
            supports_search=True,
        ),
        DataSourceInfo(
            id="ecb",
            name="European Central Bank",
            description="Eurozone monetary policy, HICP inflation, exchange rates (format: FLOW/KEY)",
            requires_api_key=False,
            supports_search=True,
        ),
    ]
    return SourcesResponse(sources=sources)


@app.get("/api/v1/series/{series_id}", response_model=SeriesResponse)
async def get_series(
    series_id: str,
    source: str = Query("fred"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    frequency: Optional[str] = Query(None),
    aggregation_method: Optional[str] = Query(None),
    units: Optional[str] = Query(None),
):
    service = get_service(source)

    t0 = time.monotonic()
    result = service.get_series(
        series_id=series_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        frequency=frequency,
        aggregation_method=aggregation_method,
        units=units,
    )
    latency_ms = int((time.monotonic() - t0) * 1000)

    params = {"source": source, "series_id": series_id}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if limit:
        params["limit"] = str(limit)
    if frequency:
        params["frequency"] = frequency
    if units:
        params["units"] = units

    fetch_id, fetched_at = record_fetch(
        source=source.lower(),
        series_id=series_id,
        request_params=params,
        response_body=result,
        latency_ms=latency_ms,
    )

    result["source"] = source.lower()
    result["fetch_id"] = fetch_id
    result["fetched_at"] = fetched_at
    return result


@app.get("/api/v1/series/{series_id}/info", response_model=SeriesInfoResponse)
async def get_series_info(series_id: str):
    fred_service = get_fred_service()
    return fred_service.get_series_info(series_id)


@app.get("/api/v1/search", response_model=SearchResponse)
async def search_series(
    q: str = Query(...),
    source: str = Query("fred"),
    limit: int = Query(20, ge=1, le=1000),
    order_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query(None),
):
    service = get_service(source)
    return service.search_series(
        search_text=q,
        limit=limit,
        order_by=order_by,
        sort_order=sort_order,
    )


@app.get("/api/v1/indicators/common", response_model=MultipleSeriesResponse)
async def get_common_indicators(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """Fetch 6 common U.S. economic indicators, each with its own provenance record."""
    common_series = ["GDP", "UNRATE", "CPIAUCSL", "FEDFUNDS", "SP500", "DGS10"]
    fred_service = get_fred_service()

    results = {}
    errors = []

    for sid in common_series:
        try:
            params: dict = {"source": "fred", "series_id": sid}
            call_kwargs: dict = {"series_id": sid}
            if start_date:
                params["start_date"] = start_date
                call_kwargs["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
                call_kwargs["end_date"] = end_date

            t0 = time.monotonic()
            raw = fred_service.get_series(**call_kwargs)
            latency_ms = int((time.monotonic() - t0) * 1000)

            fetch_id, fetched_at = record_fetch(
                source="fred",
                series_id=sid,
                request_params=params,
                response_body=raw,
                latency_ms=latency_ms,
            )

            results[sid] = SeriesInfoWithProvenance(
                title=raw.get("title", ""),
                units=raw.get("units", ""),
                frequency=raw.get("frequency", ""),
                data=raw.get("data", []),
                data_points=raw.get("data_points", 0),
                fetch_id=fetch_id,
                fetched_at=fetched_at,
            )
        except Exception as e:
            errors.append({"series_id": sid, "error": str(e)})

    return MultipleSeriesResponse(
        series=results,
        errors=errors,
        successful=len(results),
        failed=len(errors),
        source="fred",
    )


@app.post("/api/v1/series/multiple", response_model=MultipleSeriesResponse)
async def get_multiple_series(
    series_ids: List[str],
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    fred_service = get_fred_service()
    results = {}
    errors = []

    for sid in series_ids:
        try:
            params: dict = {"source": "fred", "series_id": sid}
            call_kwargs: dict = {"series_id": sid}
            if start_date:
                params["start_date"] = start_date
                call_kwargs["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
                call_kwargs["end_date"] = end_date

            t0 = time.monotonic()
            raw = fred_service.get_series(**call_kwargs)
            latency_ms = int((time.monotonic() - t0) * 1000)

            fetch_id, fetched_at = record_fetch(
                source="fred",
                series_id=sid,
                request_params=params,
                response_body=raw,
                latency_ms=latency_ms,
            )

            results[sid] = SeriesInfoWithProvenance(
                title=raw.get("title", ""),
                units=raw.get("units", ""),
                frequency=raw.get("frequency", ""),
                data=raw.get("data", []),
                data_points=raw.get("data_points", 0),
                fetch_id=fetch_id,
                fetched_at=fetched_at,
            )
        except Exception as e:
            errors.append({"series_id": sid, "error": str(e)})

    return MultipleSeriesResponse(
        series=results,
        errors=errors,
        successful=len(results),
        failed=len(errors),
    )


# Census endpoints
@app.get("/api/v1/census/datasets")
async def get_census_datasets(
    dataset_type: Optional[str] = Query(None),
):
    census_service = get_census_service()
    datasets = census_service.get_datasets(dataset_type=dataset_type)
    return {"datasets": datasets}


@app.get("/api/v1/census/datasets/{dataset}/variables")
async def get_census_variables(
    dataset: str,
    year: Optional[int] = Query(None),
):
    try:
        census_service = get_census_service()
        variables = census_service.get_variables(dataset, year=year)
        if not variables:
            return {
                "variables": [],
                "message": f"No variables found for '{dataset}'. Check Census Bureau documentation.",
            }
        return {"variables": variables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching variables: {e}")


@app.get("/api/v1/census/datasets/{dataset}/geographies")
async def get_census_geographies(dataset: str):
    census_service = get_census_service()
    geographies = census_service.get_geographies(dataset)
    return {"geographies": geographies}


@app.post("/api/v1/census/query")
async def execute_census_query(query: dict):
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
        t0 = time.monotonic()
        result = census_service.execute_query(
            dataset=dataset,
            variables=variables,
            geography=geography,
            year=year,
            time_range=time_range,
        )
        latency_ms = int((time.monotonic() - t0) * 1000)

        fetch_id, fetched_at = record_fetch(
            source="census",
            series_id=f"{dataset}:{','.join(variables)}",
            request_params={"dataset": dataset, "variables": variables, "geography": geography},
            response_body=result,
            latency_ms=latency_ms,
        )

        result["fetch_id"] = fetch_id
        result["fetched_at"] = fetched_at
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing Census query: {e}")


@app.get("/api/v1/validate/{source}")
async def validate_input(
    source: str,
    input_value: str = Query(...),
):
    service = get_service(source)
    if source in ("yfinance", "alphavantage", "edgar", "oecd", "ecb"):
        is_valid, error_message = service.validate_symbol(input_value)
    elif source == "census":
        is_valid, error_message = service.validate_variable(input_value)
    else:
        is_valid, error_message = True, None
    return {"is_valid": is_valid, "error_message": error_message, "source": source, "input": input_value}


@app.get("/api/v1/suggestions/{source}")
async def get_suggestions(
    source: str,
    q: str = Query(""),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    service = get_service(source)
    try:
        if source == "yfinance":
            suggestions = service.get_suggestions(q, limit=limit)
            results = [{"symbol": s, "type": "ticker"} for s in suggestions]
        elif source in ("alphavantage", "edgar", "oecd", "ecb"):
            suggestions = service.get_suggestions(q, category=category, limit=limit)
            results = [{"symbol": s[0], "type": s[1]} for s in suggestions]
        elif source == "census":
            suggestions = service.get_suggestions(q, category=category, limit=limit)
            results = [{"symbol": s, "type": "variable"} for s in suggestions]
        else:
            results = []
        return {"query": q, "source": source, "suggestions": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {e}")


# Provenance endpoints
@app.get("/api/v1/provenance/{fetch_id}", response_model=FetchRecord)
async def get_provenance(fetch_id: str):
    """Return the full raw fetch record for a given fetch_id."""
    record = get_fetch_record(fetch_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No fetch record found for {fetch_id}")
    return record


# AI analysis endpoint
@app.post("/api/v1/ai/analyze", response_model=AIAnalysisResponse)
async def analyze_with_ai(request: AIAnalysisRequest):
    """
    Analyze fetched data series with Claude.

    The AI receives SOURCE_BLOCKs for each fetch_id and may call fetch_series
    for additional data. It must cite specific fetch_ids for all quantitative claims.
    """
    from app.ai_service import analyze

    try:
        result = analyze(fetch_ids=request.fetch_ids, question=request.question)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc}"})
