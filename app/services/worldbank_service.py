from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
import requests
from fastapi import HTTPException


class WorldBankService:
    """Service for interacting with the World Bank API."""
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    def __init__(self):
        """Initialize World Bank service (no API key required)."""
        pass
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        country: str = "USA",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get time series data from World Bank.
        
        Args:
            series_id: Indicator code (e.g., 'NY.GDP.MKTP.CD' for GDP, 'SP.POP.TOTL' for Population)
            start_date: Start year (YYYY format, e.g., '2000')
            end_date: End year (YYYY format, e.g., '2023')
            country: Country code (default: 'USA', use 'all' for all countries)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing series data and metadata
        """
        try:
            # Parse dates to years
            start_year = None
            end_year = None
            
            if start_date:
                try:
                    start_year = int(start_date.split('-')[0])
                except:
                    start_year = int(start_date) if start_date.isdigit() else None
            
            if end_date:
                try:
                    end_year = int(end_date.split('-')[0])
                except:
                    end_year = int(end_date) if end_date.isdigit() else None
            
            # Build URL
            url = f"{self.BASE_URL}/country/{country}/indicator/{series_id}"
            params = {
                "format": "json",
                "per_page": 10000  # Get all data
            }
            
            if start_year:
                params["date"] = f"{start_year}:{end_year or datetime.now().year}"
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) < 2:
                raise ValueError(f"No data returned for indicator {series_id}")
            
            # First element is metadata, second is data
            metadata = data[0] if len(data) > 0 else {}
            records = data[1] if len(data) > 1 else []
            
            if not records:
                raise ValueError(f"No data records found for {series_id}")
            
            # Get indicator name from first record
            indicator_name = records[0].get('indicator', {}).get('value', series_id) if records else series_id
            
            # Convert to standardized format
            data_points = []
            for record in records:
                date_str = str(record.get('date', ''))
                value = record.get('value')
                
                if value is not None:
                    try:
                        data_points.append({
                            "date": f"{date_str}-01-01",  # World Bank uses years, convert to date
                            "value": float(value)
                        })
                    except (ValueError, TypeError):
                        continue
            
            # Sort by date
            data_points.sort(key=lambda x: x['date'])
            
            # Filter by date range if specified
            if start_date and len(start_date) == 10:  # Full date format
                data_points = [dp for dp in data_points if dp['date'] >= start_date]
            if end_date and len(end_date) == 10:  # Full date format
                data_points = [dp for dp in data_points if dp['date'] <= end_date]
            
            return {
                "series_id": series_id,
                "title": indicator_name,
                "units": records[0].get('indicator', {}).get('value', '') if records else '',
                "frequency": "Annual",
                "seasonal_adjustment": "Not Seasonally Adjusted",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]['date'] if data_points else "",
                "observation_end": data_points[-1]['date'] if data_points else "",
                "data": data_points,
                "data_points": len(data_points)
            }
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching World Bank series {series_id}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing World Bank series {series_id}: {str(e)}"
            )
    
    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search World Bank indicators.
        Note: order_by and sort_order are ignored as World Bank API doesn't support them.
        """
        try:
            url = f"{self.BASE_URL}/indicator"
            params = {
                "format": "json",
                "per_page": limit,
                "q": search_text
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) < 2:
                return {
                    "query": search_text,
                    "results": [],
                    "count": 0
                }
            
            records = data[1] if len(data) > 1 else []
            
            results = []
            for record in records[:limit]:
                results.append({
                    "series_id": record.get('id', ''),
                    "title": record.get('name', ''),
                    "units": "",
                    "frequency": "Annual",
                    "seasonal_adjustment": "Not Seasonally Adjusted",
                    "popularity": 0
                })
            
            # Apply client-side sorting if requested (World Bank API doesn't support server-side sorting)
            if order_by and sort_order:
                if order_by == "title":
                    results.sort(key=lambda x: x.get('title', '').lower(), reverse=(sort_order == "desc"))
                elif order_by == "series_id":
                    results.sort(key=lambda x: x.get('series_id', '').lower(), reverse=(sort_order == "desc"))
            
            return {
                "query": search_text,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching World Bank: {str(e)}"
            )


# Global service instance (lazy initialization)
_worldbank_service: Optional[WorldBankService] = None


def get_worldbank_service() -> WorldBankService:
    """Get or create World Bank service instance."""
    global _worldbank_service
    if _worldbank_service is None:
        _worldbank_service = WorldBankService()
    return _worldbank_service

