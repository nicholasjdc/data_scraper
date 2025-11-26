from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import yfinance as yf
from fastapi import HTTPException

from app.data.yfinance_symbols import (
    validate_symbol_format,
    search_symbols as search_yfinance_symbols,
    ALL_SYMBOLS as YFINANCE_ALL_SYMBOLS
)


class YFinanceService:
    """Service for interacting with Yahoo Finance data via yfinance library."""
    
    def __init__(self):
        """Initialize YFinance service (no API key required)."""
        pass
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None,
        interval: str = "1d",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get time series data from Yahoo Finance.
        
        Args:
            series_id: Ticker symbol (e.g., 'AAPL', 'MSFT', '^GSPC' for S&P 500)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            period: Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing series data and metadata
        """
        try:
            ticker = yf.Ticker(series_id)
            
            # Fetch historical data
            if start_date and end_date:
                hist = ticker.history(start=start_date, end=end_date, interval=interval)
            elif period:
                hist = ticker.history(period=period, interval=interval)
            else:
                # Default to 1 year if no dates specified
                hist = ticker.history(period="1y", interval=interval)
            
            if hist is None or hist.empty:
                raise ValueError(f"No data returned for {series_id}")
            
            # Get ticker info for metadata
            try:
                info = ticker.info
                title = info.get('longName', info.get('shortName', series_id))
            except:
                title = series_id
            
            # Use 'Close' price as the value
            series = hist['Close']
            
            # Convert to standardized format
            data_points = []
            for date, value in series.items():
                date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date)
                
                data_points.append({
                    "date": date_str,
                    "value": float(value) if pd.notna(value) else None
                })
            
            # Sort by date
            data_points.sort(key=lambda x: x['date'])
            
            return {
                "series_id": series_id,
                "title": title,
                "units": "Price",
                "frequency": "Daily" if interval == "1d" else interval,
                "seasonal_adjustment": "Not Seasonally Adjusted",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]['date'] if data_points else "",
                "observation_end": data_points[-1]['date'] if data_points else "",
                "data": data_points,
                "data_points": len(data_points)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching Yahoo Finance series {series_id}: {str(e)}"
            )
    
    def validate_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate ticker symbol format.
        Returns (is_valid, error_message).
        """
        if not symbol or not symbol.strip():
            return False, "Symbol cannot be empty"
        
        if not validate_symbol_format(symbol):
            return False, f"Invalid symbol format: {symbol}. Symbols should be uppercase alphanumeric (e.g., AAPL, MSFT, ^GSPC)"
        
        return True, None
    
    def get_suggestions(self, query: str, limit: int = 20) -> List[str]:
        """
        Get symbol suggestions based on query.
        """
        return search_yfinance_symbols(query, limit=limit)
    
    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search is not directly supported by yfinance.
        Returns a message indicating manual ticker lookup is required.
        """
        return {
            "query": search_text,
            "results": [],
            "count": 0,
            "message": "Yahoo Finance does not support programmatic search. Please use ticker symbols (e.g., AAPL, MSFT, ^GSPC for S&P 500)."
        }


# Global service instance (lazy initialization)
_yfinance_service: Optional[YFinanceService] = None


def get_yfinance_service() -> YFinanceService:
    """Get or create YFinance service instance."""
    global _yfinance_service
    if _yfinance_service is None:
        _yfinance_service = YFinanceService()
    return _yfinance_service

