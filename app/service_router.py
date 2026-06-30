from fastapi import HTTPException


def get_service(source: str):
    """Route a source name to its service instance."""
    source = (source or "fred").lower()

    if source == "fred":
        from app.services.fred_service import get_fred_service
        return get_fred_service()
    elif source == "alphavantage":
        from app.services.alphavantage_service import get_alphavantage_service
        return get_alphavantage_service()
    elif source == "yfinance":
        from app.services.yfinance_service import get_yfinance_service
        return get_yfinance_service()
    elif source == "worldbank":
        from app.services.worldbank_service import get_worldbank_service
        return get_worldbank_service()
    elif source == "census":
        from app.services.census_service import get_census_service
        return get_census_service()
    elif source == "edgar":
        from app.services.edgar_service import get_edgar_service
        return get_edgar_service()
    elif source == "oecd":
        from app.services.oecd_service import get_oecd_service
        return get_oecd_service()
    elif source == "ecb":
        from app.services.ecb_service import get_ecb_service
        return get_ecb_service()
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source: {source}. Available: fred, alphavantage, yfinance, worldbank, census, edgar, oecd, ecb",
        )
