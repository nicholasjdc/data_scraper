from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from fastapi import HTTPException

from app.config import settings
from app.data.alphavantage_symbols import (
    validate_symbol_format,
    search_symbols as search_alphavantage_symbols,
)


class AlphaVantageService:
    """Service for interacting with the Alpha Vantage API."""
    
    def __init__(self):
        """Initialize Alpha Vantage client with API key."""
        if not settings.alpha_vantage_api_key:
            raise ValueError(
                "ALPHA_VANTAGE_API_KEY not found. Please set it as an environment variable "
                "or in a .env file."
            )
        self.api_key = settings.alpha_vantage_api_key
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')
        self.fx = ForeignExchange(key=self.api_key, output_format='pandas')
        self.cc = CryptoCurrencies(key=self.api_key, output_format='pandas')
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        function: str = "TIME_SERIES_DAILY",
        symbol: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get time series data from Alpha Vantage.
        
        Args:
            series_id: Symbol or identifier (e.g., 'AAPL', 'EUR/USD', 'BTC')
            start_date: Start date in YYYY-MM-DD format (filtered client-side)
            end_date: End date in YYYY-MM-DD format (filtered client-side)
            function: API function (TIME_SERIES_DAILY, FX_DAILY, CRYPTO_INTRADAY, etc.)
            symbol: Alternative symbol parameter (if series_id not used)
            **kwargs: Additional parameters for specific functions
        
        Returns:
            Dictionary containing series data and metadata
        """
        try:
            symbol = symbol or series_id
            
            # Determine data type and fetch accordingly
            # Note: outputsize='full' is a premium feature, using 'compact' for free tier
            if function.startswith("FX_"):
                # Forex data
                if function == "FX_DAILY":
                    data, meta = self.fx.get_currency_exchange_daily(
                        from_symbol=symbol.split('/')[0] if '/' in symbol else symbol[:3],
                        to_symbol=symbol.split('/')[1] if '/' in symbol else symbol[3:],
                        outputsize='compact'  # Changed from 'full' to 'compact' (free tier)
                    )
                else:
                    raise ValueError(f"Unsupported FX function: {function}")
            elif function.startswith("CRYPTO"):
                # Cryptocurrency data
                if function == "CRYPTO_INTRADAY":
                    data, meta = self.cc.get_crypto_intraday(
                        symbol=symbol,
                        market='USD',
                        interval='60min',
                        outputsize='compact'  # Changed from 'full' to 'compact' (free tier)
                    )
                elif function == "DIGITAL_CURRENCY_DAILY":
                    data, meta = self.cc.get_digital_currency_daily(
                        symbol=symbol,
                        market='USD'
                    )
                else:
                    raise ValueError(f"Unsupported crypto function: {function}")
            else:
                # Stock data
                if function == "TIME_SERIES_DAILY":
                    data, meta = self.ts.get_daily(symbol=symbol, outputsize='compact')  # Changed from 'full' to 'compact' (free tier)
                elif function == "TIME_SERIES_INTRADAY":
                    interval = kwargs.get('interval', '60min')
                    data, meta = self.ts.get_intraday(symbol=symbol, interval=interval, outputsize='compact')  # Changed from 'full' to 'compact' (free tier)
                elif function == "TIME_SERIES_WEEKLY":
                    data, meta = self.ts.get_weekly(symbol=symbol)
                elif function == "TIME_SERIES_MONTHLY":
                    data, meta = self.ts.get_monthly(symbol=symbol)
                else:
                    raise ValueError(f"Unsupported function: {function}")
            
            # Convert to standardized format
            # Alpha Vantage returns data with date as index and OHLCV columns
            # We'll use the 'close' price as the value
            if data is None or data.empty:
                raise ValueError(f"No data returned for {series_id}")
            
            # Extract close prices (or 4. close for forex)
            if 'close' in data.columns:
                series = data['close']
            elif '4. close' in data.columns:
                series = data['4. close']
            else:
                # Use first numeric column
                numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
                if len(numeric_cols) > 0:
                    series = data[numeric_cols[0]]
                else:
                    raise ValueError("No numeric data columns found")
            
            # Convert to dict with date strings
            data_points = []
            for date, value in series.items():
                date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date)
                
                # Apply date filtering
                if start_date and date_str < start_date:
                    continue
                if end_date and date_str > end_date:
                    continue
                
                data_points.append({
                    "date": date_str,
                    "value": float(value) if pd.notna(value) else None
                })
            
            # Sort by date
            data_points.sort(key=lambda x: x['date'])
            
            return {
                "series_id": series_id,
                "title": meta.get('2. Symbol', series_id) if isinstance(meta, dict) else f"{series_id} ({function})",
                "units": "Price",
                "frequency": "Daily" if "DAILY" in function else "Intraday" if "INTRADAY" in function else "Unknown",
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
                detail=f"Error fetching Alpha Vantage series {series_id}: {str(e)}"
            )
    
    def validate_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate symbol format.
        Returns (is_valid, error_message).
        """
        if not symbol or not symbol.strip():
            return False, "Symbol cannot be empty"
        
        is_valid, symbol_type = validate_symbol_format(symbol)
        if not is_valid:
            if '/' in symbol:
                return False, f"Invalid forex pair format: {symbol}. Use format XXX/YYY (e.g., EUR/USD, GBP/USD)"
            else:
                return False, f"Invalid symbol format: {symbol}. Use stock symbols (e.g., AAPL) or crypto (e.g., BTC)"
        
        return True, None
    
    def get_suggestions(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[Tuple[str, str]]:
        """
        Get symbol suggestions based on query.
        Returns list of (symbol, type) tuples.
        """
        return search_alphavantage_symbols(query, category=category, limit=limit)
    
    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search is not directly supported by Alpha Vantage API.
        Returns a message indicating manual symbol lookup is required.
        """
        return {
            "query": search_text,
            "results": [],
            "count": 0,
            "message": "Alpha Vantage does not support search. Please use stock symbols (e.g., AAPL, MSFT) or forex pairs (e.g., EUR/USD)."
        }


# Global service instance (lazy initialization)
_alphavantage_service: Optional[AlphaVantageService] = None


def get_alphavantage_service() -> Optional[AlphaVantageService]:
    """Get or create Alpha Vantage service instance."""
    global _alphavantage_service
    if _alphavantage_service is None:
        try:
            _alphavantage_service = AlphaVantageService()
        except ValueError:
            # API key not configured, return None
            return None
    return _alphavantage_service

