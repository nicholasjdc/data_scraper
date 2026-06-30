"""
Alpha Vantage service — forex only.

The free tier is 25 requests/day, which is too limited for stock or crypto
data when yfinance covers those without a daily cap. This service is kept
for FX_DAILY (clean historical forex rates) which yfinance handles poorly.

Accepted series_id formats:
  EUR/USD   — from_symbol / to_symbol  (slash delimiter)
  EURUSD    — 3+3 letter concat (split at position 3)
"""
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from fastapi import HTTPException

from app.config import settings


_FOREX_EXAMPLES = [
    ("EUR/USD", "forex"), ("GBP/USD", "forex"), ("USD/JPY", "forex"),
    ("USD/CHF", "forex"), ("AUD/USD", "forex"), ("USD/CAD", "forex"),
    ("NZD/USD", "forex"), ("EUR/GBP", "forex"), ("EUR/JPY", "forex"),
    ("GBP/JPY", "forex"), ("USD/CNY", "forex"), ("USD/KRW", "forex"),
    ("USD/INR", "forex"), ("USD/BRL", "forex"), ("USD/MXN", "forex"),
    ("USD/ZAR", "forex"), ("EUR/CHF", "forex"), ("EUR/AUD", "forex"),
]

_MAJOR_CURRENCIES = {
    "EUR", "USD", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD",
    "CNY", "HKD", "SGD", "SEK", "NOK", "DKK", "MXN", "BRL",
    "ZAR", "KRW", "INR", "RUB", "TRY", "PLN", "CZK", "HUF",
}


def _parse_fx_pair(series_id: str) -> Tuple[str, str]:
    """Return (from_symbol, to_symbol) or raise ValueError."""
    s = series_id.upper().strip()
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 2 and all(len(p) == 3 for p in parts):
            return parts[0], parts[1]
    if len(s) == 6:
        return s[:3], s[3:]
    raise ValueError(
        f"Invalid forex pair '{series_id}'. "
        "Use format XXX/YYY (e.g. EUR/USD) or XXXYYY (e.g. EURUSD)."
    )


class AlphaVantageService:
    """Alpha Vantage forex service (FX_DAILY only)."""

    def __init__(self):
        if not settings.alpha_vantage_api_key:
            raise ValueError(
                "ALPHA_VANTAGE_API_KEY not found. "
                "Set it in .env or as an environment variable."
            )
        self.fx = ForeignExchange(
            key=settings.alpha_vantage_api_key, output_format="pandas"
        )

    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        try:
            from_sym, to_sym = _parse_fx_pair(series_id)

            data, _meta = self.fx.get_currency_exchange_daily(
                from_symbol=from_sym,
                to_symbol=to_sym,
                outputsize="full",
            )

            if data is None or data.empty:
                raise ValueError(f"No data returned for {series_id}")

            close_col = next(
                (c for c in data.columns if "close" in c.lower()), None
            )
            if close_col is None:
                raise ValueError(f"No close-price column in response for {series_id}")

            series = data[close_col]
            data_points = []
            for date, value in series.items():
                date_str = (
                    date.strftime("%Y-%m-%d")
                    if isinstance(date, pd.Timestamp)
                    else str(date)
                )
                if start_date and date_str < start_date:
                    continue
                if end_date and date_str > end_date:
                    continue
                if pd.notna(value):
                    data_points.append({"date": date_str, "value": float(value)})

            data_points.sort(key=lambda x: x["date"])

            return {
                "series_id": series_id,
                "title": f"{from_sym}/{to_sym} Exchange Rate",
                "units": to_sym,
                "frequency": "Daily",
                "seasonal_adjustment": "Not Seasonally Adjusted",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]["date"] if data_points else "",
                "observation_end": data_points[-1]["date"] if data_points else "",
                "data": data_points,
                "data_points": len(data_points),
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching Alpha Vantage forex {series_id}: {e}",
            )

    def validate_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        try:
            _parse_fx_pair(symbol)
            return True, None
        except ValueError as e:
            return False, str(e)

    def get_suggestions(
        self, query: str, category: Optional[str] = None, limit: int = 20
    ) -> List[Tuple[str, str]]:
        q = query.upper()
        return [
            pair for pair in _FOREX_EXAMPLES if q in pair[0]
        ][:limit]

    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        q = search_text.upper()
        matches = [p[0] for p in _FOREX_EXAMPLES if q in p[0]][:limit]
        return {
            "query": search_text,
            "results": [
                {
                    "series_id": sym,
                    "title": f"{sym[:3]}/{sym[3:] if '/' not in sym else sym.split('/')[1]} Exchange Rate",
                    "units": "Exchange Rate",
                    "frequency": "Daily",
                    "seasonal_adjustment": "Not Seasonally Adjusted",
                    "popularity": 0,
                }
                for sym in matches
            ],
            "count": len(matches),
            "message": (
                "Alpha Vantage is used for forex only (e.g. EUR/USD, GBP/USD). "
                "For stocks use Yahoo Finance; for crypto consider FRED commodity indices."
            ),
        }


_alphavantage_service: Optional[AlphaVantageService] = None


def get_alphavantage_service() -> Optional[AlphaVantageService]:
    global _alphavantage_service
    if _alphavantage_service is None:
        try:
            _alphavantage_service = AlphaVantageService()
        except ValueError:
            return None
    return _alphavantage_service
