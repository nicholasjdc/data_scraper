from datetime import datetime
from typing import Optional, Dict, Any, List
import pandas as pd
from fredapi import Fred
from fastapi import HTTPException

from app.config import settings


class FredService:
    """Service for interacting with the FRED API."""
    
    def __init__(self):
        """Initialize FRED client with API key."""
        if not settings.fred_api_key:
            raise ValueError(
                "FRED_API_KEY not found. Please set it as an environment variable "
                "or in a .env file."
            )
        self.fred = Fred(api_key=settings.fred_api_key)
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        frequency: Optional[str] = None,
        aggregation_method: Optional[str] = None,
        units: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get economic data series from FRED.
        
        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of observations
            frequency: Data frequency (e.g., 'd', 'w', 'm', 'q', 'a')
            aggregation_method: Aggregation method ('avg', 'sum', 'eop')
            units: Data units ('lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log')
        
        Returns:
            Dictionary containing series data and metadata
        """
        try:
            # Build parameters
            params = {}
            if start_date:
                params['observation_start'] = start_date
            if end_date:
                params['observation_end'] = end_date
            if limit:
                params['limit'] = limit
            if frequency:
                params['frequency'] = frequency
            if aggregation_method:
                params['aggregation_method'] = aggregation_method
            if units:
                params['units'] = units
            
            # Fetch data
            data = self.fred.get_series(series_id, **params)
            
            # Get series info
            info = self.fred.get_series_info(series_id)
            
            # Convert to dict format
            result = {
                "series_id": series_id,
                "title": info.get('title', ''),
                "units": info.get('units', ''),
                "frequency": info.get('frequency', ''),
                "seasonal_adjustment": info.get('seasonal_adjustment', ''),
                "last_updated": info.get('last_updated', ''),
                "observation_start": info.get('observation_start', ''),
                "observation_end": info.get('observation_end', ''),
                "data": [
                    {
                        "date": str(date),
                        "value": float(value) if pd.notna(value) else None
                    }
                    for date, value in data.items()
                ],
                "data_points": len(data)
            }
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching FRED series {series_id}: {str(e)}"
            )
    
    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for economic data series.
        
        Args:
            search_text: Search query
            limit: Maximum number of results
            order_by: Order by field ('search_rank', 'series_id', 'title', 'units', 'frequency')
            sort_order: Sort order ('asc' or 'desc')
        
        Returns:
            Dictionary containing search results
        """
        try:
            # FRED API parameters
            search_params = {
                "limit": limit
            }
            # Only add order_by and sort_order if provided (FRED supports these)
            if order_by:
                search_params["order_by"] = order_by
            if sort_order:
                search_params["sort_order"] = sort_order
            
            results = self.fred.search(
                search_text,
                **search_params
            )
            
            # Handle case when search returns no results
            if results is None or results.empty:
                return {
                    "query": search_text,
                    "results": [],
                    "count": 0
                }
            
            return {
                "query": search_text,
                "results": [
                    {
                        "series_id": row.get('id', ''),
                        "title": row.get('title', ''),
                        "units": row.get('units', ''),
                        "frequency": row.get('frequency', ''),
                        "seasonal_adjustment": row.get('seasonal_adjustment', ''),
                        "popularity": row.get('popularity', 0)
                    }
                    for _, row in results.iterrows()
                ],
                "count": len(results)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching FRED: {str(e)}"
            )
    
    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata about a FRED series.
        
        Args:
            series_id: FRED series ID
        
        Returns:
            Dictionary containing series metadata
        """
        try:
            info = self.fred.get_series_info(series_id)
            
            return {
                "series_id": info.get('id', series_id),
                "title": info.get('title', ''),
                "observation_start": info.get('observation_start', ''),
                "observation_end": info.get('observation_end', ''),
                "frequency": info.get('frequency', ''),
                "frequency_short": info.get('frequency_short', ''),
                "units": info.get('units', ''),
                "units_short": info.get('units_short', ''),
                "seasonal_adjustment": info.get('seasonal_adjustment', ''),
                "seasonal_adjustment_short": info.get('seasonal_adjustment_short', ''),
                "last_updated": info.get('last_updated', ''),
                "popularity": info.get('popularity', 0),
                "notes": info.get('notes', '')
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching series info for {series_id}: {str(e)}"
            )
    
    def get_multiple_series(
        self,
        series_ids: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get multiple economic data series at once.
        
        Args:
            series_ids: List of FRED series IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Dictionary containing data for all series
        """
        try:
            results = {}
            errors = []
            
            for series_id in series_ids:
                try:
                    params = {}
                    if start_date:
                        params['observation_start'] = start_date
                    if end_date:
                        params['observation_end'] = end_date
                    
                    data = self.fred.get_series(series_id, **params)
                    info = self.fred.get_series_info(series_id)
                    
                    results[series_id] = {
                        "title": info.get('title', ''),
                        "units": info.get('units', ''),
                        "frequency": info.get('frequency', ''),
                        "data": [
                            {
                                "date": str(date),
                                "value": float(value) if pd.notna(value) else None
                            }
                            for date, value in data.items()
                        ],
                        "data_points": len(data)
                    }
                except Exception as e:
                    errors.append({
                        "series_id": series_id,
                        "error": str(e)
                    })
            
            return {
                "series": results,
                "errors": errors,
                "successful": len(results),
                "failed": len(errors)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching multiple series: {str(e)}"
            )


# Global service instance (lazy initialization)
_fred_service: Optional[FredService] = None


def get_fred_service() -> FredService:
    """Get or create FRED service instance."""
    global _fred_service
    if _fred_service is None:
        _fred_service = FredService()
    return _fred_service

