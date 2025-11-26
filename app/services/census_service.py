from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import requests
from fastapi import HTTPException

from app.data.census_variables import (
    validate_variable_format,
    search_variables as search_census_variables,
)


class CensusService:
    """Service for interacting with the U.S. Census Bureau API."""
    
    BASE_URL = "https://api.census.gov/data"
    
    # Common datasets
    YEAR_BASED_DATASETS = [
        {"id": "pep/population", "name": "Population Estimates Program", "years": list(range(2010, 2025))},
        {"id": "acs/acs5", "name": "American Community Survey 5-Year", "years": list(range(2010, 2024))},
        {"id": "acs/acs1", "name": "American Community Survey 1-Year", "years": list(range(2010, 2024))},
        {"id": "dec/pl", "name": "Decennial Census - Population", "years": [2020, 2010, 2000]},
    ]
    
    TIMESERIES_DATASETS = [
        {"id": "timeseries/eits/mid", "name": "Economic Indicators - Monthly/Quarterly/Annual"},
        {"id": "timeseries/eits/retail", "name": "Retail Trade"},
        {"id": "timeseries/eits/manufacturing", "name": "Manufacturing"},
        {"id": "timeseries/eits/construction", "name": "Construction"},
    ]
    
    # Common geography types
    GEOGRAPHY_TYPES = [
        {"id": "us:1", "name": "United States", "level": "national"},
        {"id": "state:*", "name": "All States", "level": "state"},
        {"id": "county:*", "name": "All Counties", "level": "county"},
        {"id": "tract:*", "name": "All Census Tracts", "level": "tract"},
    ]
    
    def __init__(self):
        """Initialize Census service (no API key required for most endpoints)."""
        pass
    
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dataset: str = "timeseries/eits/mid",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get time series data from U.S. Census Bureau.
        
        Args:
            series_id: Series code or variable name
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            dataset: Dataset name (default: 'timeseries/eits/mid' for Economic Indicators)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing series data and metadata
        
        Note: Common datasets:
        - timeseries/eits/mid: Economic Indicators Time Series (Monthly, Quarterly, Annual)
        - timeseries/eits/retail: Retail Trade
        - timeseries/eits/manufacturing: Manufacturing
        - acs/acs5: American Community Survey 5-Year Estimates
        """
        try:
            # Build URL
            url = f"{self.BASE_URL}/{dataset}"
            params = {
                "get": series_id,
                "for": "us:1",
                "time": "from+2000+to+2024"  # Default time range
            }
            
            # Parse dates
            if start_date:
                try:
                    start_year = int(start_date.split('-')[0])
                    params["time"] = f"from+{start_year}"
                except:
                    pass
            
            if end_date:
                try:
                    end_year = int(end_date.split('-')[0])
                    if "from" in params.get("time", ""):
                        params["time"] = f"{params['time']}+to+{end_year}"
                    else:
                        params["time"] = f"to+{end_year}"
                except:
                    pass
            
            response = requests.get(url, params=params, timeout=30)
            
            # Check for 404 or other errors
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Variable '{series_id}' not found in dataset '{dataset}'. Please verify the variable name exists in this dataset. You can browse available datasets and variables at https://www.census.gov/data/developers/data-sets.html"
                )
            
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                data = response.json()
            except ValueError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid JSON response from Census Bureau API. Response text: {response.text[:200]}"
                )
            
            # Check if response is an error message
            if isinstance(data, dict) and 'error' in data:
                error_msg = data.get('error', 'Unknown error')
                raise HTTPException(
                    status_code=400,
                    detail=f"Census Bureau API error: {error_msg}"
                )
            
            if not data or not isinstance(data, list) or len(data) < 2:
                raise HTTPException(
                    status_code=500,
                    detail=f"No data returned for series {series_id}. Response: {str(data)[:200]}"
                )
            
            # First row is headers, rest is data
            headers = data[0]
            rows = data[1:]
            
            if not isinstance(headers, list):
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected response format. Expected list of headers, got: {type(headers)}"
                )
            
            # Find time and value columns
            time_idx = headers.index('time') if 'time' in headers else None
            value_idx = headers.index(series_id) if series_id in headers else None
            
            if time_idx is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"Time column not found in response. Available columns: {', '.join(headers)}"
                )
            
            if value_idx is None:
                available_vars = [h for h in headers if h not in ['time', 'for', 'us', 'NAME', 'GEO_ID']]
                available_msg = f" Available variables in this dataset: {', '.join(available_vars[:10])}" if available_vars else ""
                raise HTTPException(
                    status_code=404,
                    detail=f"Variable '{series_id}' not found in dataset '{dataset}'.{available_msg} Please verify the variable name at https://www.census.gov/data/developers/data-sets.html"
                )
            
            # Convert to standardized format
            data_points = []
            for row in rows:
                if len(row) <= max(time_idx, value_idx):
                    continue
                
                time_str = row[time_idx]
                try:
                    value = float(row[value_idx]) if row[value_idx] else None
                except (ValueError, TypeError):
                    value = None
                
                if value is not None and time_str:
                    # Convert time string to date (format varies by dataset)
                    date_str = self._parse_census_date(time_str)
                    
                    # Filter by date range if specified
                    if start_date and date_str < start_date:
                        continue
                    if end_date and date_str > end_date:
                        continue
                    
                    data_points.append({
                        "date": date_str,
                        "value": value
                    })
            
            # Sort by date
            data_points.sort(key=lambda x: x['date'])
            
            return {
                "series_id": series_id,
                "title": f"Census Bureau: {series_id}",
                "units": "",
                "frequency": "Monthly" if dataset.startswith("timeseries") else "Annual",
                "seasonal_adjustment": "Not Seasonally Adjusted",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]['date'] if data_points else "",
                "observation_end": data_points[-1]['date'] if data_points else "",
                "data": data_points,
                "data_points": len(data_points)
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise
        except requests.RequestException as e:
            error_msg = str(e) if str(e) else f"HTTP {getattr(e, 'response', None) and getattr(e.response, 'status_code', 'unknown')}"
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching Census Bureau series {series_id}: {error_msg}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing Census Bureau series {series_id}: {str(e) if str(e) else 'Invalid data format'}"
            )
        except Exception as e:
            # Get more details about the exception
            error_type = type(e).__name__
            error_msg = str(e) if str(e) else f"{error_type} occurred"
            import traceback
            traceback_str = traceback.format_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error processing Census Bureau series {series_id}: {error_msg}"
            )
    
    def _parse_census_date(self, time_str: str) -> str:
        """Parse Census Bureau time string to YYYY-MM-DD format."""
        try:
            # Try different formats
            if len(time_str) == 4:  # Year only
                return f"{time_str}-01-01"
            elif len(time_str) == 6:  # YYYYMM
                return f"{time_str[:4]}-{time_str[4:6]}-01"
            elif len(time_str) == 8:  # YYYYMMDD
                return f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]}"
            elif '-' in time_str:
                return time_str[:10]  # Already in date format
            else:
                return time_str
        except:
            return time_str
    
    def get_datasets(self, dataset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available datasets.
        
        Args:
            dataset_type: 'year_based' or 'timeseries' to filter, None for all
        
        Returns:
            List of dataset information dictionaries
        """
        datasets = []
        
        if dataset_type is None or dataset_type == "year_based":
            datasets.extend(self.YEAR_BASED_DATASETS)
        
        if dataset_type is None or dataset_type == "timeseries":
            datasets.extend(self.TIMESERIES_DATASETS)
        
        return datasets
    
    def get_variables(self, dataset: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get available variables for a dataset.
        
        Args:
            dataset: Dataset identifier (e.g., 'pep/population', 'timeseries/eits/mid')
            year: Year for year-based datasets
        
        Returns:
            List of variable information dictionaries
        """
        variables_found = []
        
        # Try to fetch variables from API
        try:
            if dataset.startswith("timeseries"):
                # For timeseries, try to get a sample response to see available variables
                url = f"{self.BASE_URL}/{dataset}"
                
                # Try with a known variable first to get the structure
                # For eits datasets, try EMPSALUS
                if "eits" in dataset:
                    test_params = {"get": "EMPSALUS", "for": "us:1", "time": "from+2023+to+2023"}
                else:
                    # For other timeseries, try NAME first
                    test_params = {"get": "NAME", "for": "us:1", "time": "from+2023+to+2023"}
                
                response = requests.get(url, params=test_params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        headers = data[0]
                        # Filter out metadata columns
                        exclude_cols = {'time', 'for', 'us', 'NAME', 'GEO_ID', 'state', 'county', 'tract', 'block group'}
                        variables = [h for h in headers if h not in exclude_cols]
                        if variables:
                            variables_found = [{"id": v, "name": v, "description": ""} for v in variables[:100]]
            else:
                # For year-based datasets, try variables.json endpoint first
                if not year:
                    # Try most recent year
                    dataset_info = next((d for d in self.YEAR_BASED_DATASETS if d["id"] == dataset), None)
                    if dataset_info and dataset_info.get("years"):
                        year = max(dataset_info["years"])
                    else:
                        # Default to a recent year
                        year = 2023
                
                # Try the variables.json endpoint
                url = f"{self.BASE_URL}/{year}/{dataset}/variables.json"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "variables" in data:
                        vars_dict = data["variables"]
                        # Filter out geography and metadata variables
                        exclude_vars = {'NAME', 'GEO_ID', 'state', 'county', 'tract', 'block group', 'for'}
                        variables_found = [
                            {
                                "id": var_id,
                                "name": var_info.get("label", var_id),
                                "description": var_info.get("concept", "")
                            }
                            for var_id, var_info in vars_dict.items()
                            if var_id not in exclude_vars
                        ][:200]
                
                # If variables.json doesn't work, try making a sample query
                if not variables_found:
                    test_url = f"{self.BASE_URL}/{year}/{dataset}"
                    # Try with common variables based on dataset type
                    if "pep" in dataset:
                        test_params = {"get": "POP,NAME", "for": "us:1"}
                    elif "acs" in dataset:
                        test_params = {"get": "B01001_001E,NAME", "for": "us:1"}
                    else:
                        # Try with just NAME to see what's available
                        test_params = {"get": "NAME", "for": "us:1"}
                    
                    test_response = requests.get(test_url, params=test_params, timeout=10)
                    if test_response.status_code == 200:
                        test_data = test_response.json()
                        if isinstance(test_data, list) and len(test_data) > 0:
                            headers = test_data[0]
                            exclude_cols = {'NAME', 'GEO_ID', 'for', 'us', 'state', 'county'}
                            variables = [h for h in headers if h not in exclude_cols]
                            if variables:
                                variables_found = [{"id": v, "name": v, "description": ""} for v in variables[:100]]
        except Exception as e:
            # Log the error but continue to fallback
            import logging
            logging.warning(f"Error fetching variables for {dataset} (year={year}): {str(e)}")
        
        # If we found variables from API, return them
        if variables_found:
            return variables_found
        
        # Fallback: return common variables based on dataset
        # Always return fallback variables so users have something to work with
        if "pep" in dataset:
            return [
                {"id": "POP", "name": "Population", "description": "Total population"},
                {"id": "BIRTHS", "name": "Births", "description": "Number of births"},
                {"id": "DEATHS", "name": "Deaths", "description": "Number of deaths"},
                {"id": "NATURALINC", "name": "Natural Increase", "description": "Natural population increase"},
            ]
        elif "acs" in dataset:
            return [
                {"id": "B01001_001E", "name": "Total Population", "description": "Total population"},
                {"id": "B19013_001E", "name": "Median Household Income", "description": "Median household income"},
                {"id": "B25064_001E", "name": "Median Gross Rent", "description": "Median gross rent"},
                {"id": "B25077_001E", "name": "Median Home Value", "description": "Median home value"},
                {"id": "B08301_001E", "name": "Means of Transportation to Work", "description": "Commuting data"},
            ]
        elif "timeseries" in dataset:
            if "eits" in dataset:
                return [
                    {"id": "EMPSALUS", "name": "Employment and Salaries - US", "description": ""},
                    {"id": "EMPSALUSM", "name": "Employment and Salaries - US Monthly", "description": ""},
                    {"id": "RETAILUS", "name": "Retail Trade - US", "description": ""},
                    {"id": "RETAILUSM", "name": "Retail Trade - US Monthly", "description": ""},
                    {"id": "MANUFUS", "name": "Manufacturing - US", "description": ""},
                    {"id": "MANUFUSM", "name": "Manufacturing - US Monthly", "description": ""},
                ]
            else:
                return [
                    {"id": "EMPSALUS", "name": "Employment and Salaries - US", "description": ""},
                    {"id": "RETAILUS", "name": "Retail Trade - US", "description": ""},
                ]
        
        # If we can't determine the dataset type, return empty
        return []
    
    def get_geographies(self, dataset: str) -> List[Dict[str, Any]]:
        """
        Get available geography types for a dataset.
        
        Args:
            dataset: Dataset identifier
        
        Returns:
            List of geography information dictionaries
        """
        return self.GEOGRAPHY_TYPES
    
    def execute_query(
        self,
        dataset: str,
        variables: List[str],
        geography: str = "us:1",
        year: Optional[int] = None,
        time_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a Census API query.
        
        Args:
            dataset: Dataset identifier
            variables: List of variable names to fetch
            geography: Geography filter (e.g., 'us:1', 'state:*', 'state:06')
            year: Year for year-based datasets
            time_range: Dict with 'start' and 'end' for timeseries datasets
        
        Returns:
            Dictionary containing query results
        """
        try:
            # Build URL based on dataset type
            if dataset.startswith("timeseries"):
                url = f"{self.BASE_URL}/{dataset}"
                params = {
                    "get": ",".join(variables),
                    "for": geography
                }
                if time_range:
                    start_year = time_range.get("start", "2020").split("-")[0]
                    end_year = time_range.get("end", "2024").split("-")[0]
                    params["time"] = f"from+{start_year}+to+{end_year}"
                else:
                    params["time"] = "from+2020+to+2024"
            else:
                # Year-based dataset
                if not year:
                    # Try to get most recent year
                    dataset_info = next((d for d in self.YEAR_BASED_DATASETS if d["id"] == dataset), None)
                    if dataset_info and dataset_info.get("years"):
                        year = max(dataset_info["years"])
                    else:
                        year = 2023
                
                url = f"{self.BASE_URL}/{year}/{dataset}"
                params = {
                    "get": ",".join(variables),
                    "for": geography
                }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Dataset '{dataset}' not found. Please verify the dataset name."
                )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Check for error response
            if isinstance(data, dict) and 'error' in data:
                error_msg = data.get('error', 'Unknown error')
                raise HTTPException(
                    status_code=400,
                    detail=f"Census Bureau API error: {error_msg}"
                )
            
            if not data or not isinstance(data, list) or len(data) < 2:
                raise HTTPException(
                    status_code=500,
                    detail=f"No data returned. Response: {str(data)[:200]}"
                )
            
            # Parse response
            headers = data[0]
            rows = data[1:]
            
            # Convert to structured format
            results = []
            for row in rows:
                if len(row) != len(headers):
                    continue
                
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i]
                results.append(row_dict)
            
            return {
                "dataset": dataset,
                "year": year,
                "geography": geography,
                "variables": variables,
                "headers": headers,
                "data": results,
                "count": len(results)
            }
            
        except HTTPException:
            raise
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching Census data: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing Census query: {str(e)}"
            )
    
    def get_series_by_year(
        self,
        year: int,
        dataset: str,
        variables: List[str],
        geography: str = "us:1"
    ) -> Dict[str, Any]:
        """
        Get year-based Census data.
        
        Args:
            year: Year for the dataset
            dataset: Dataset identifier (e.g., 'pep/population', 'acs/acs5')
            variables: List of variable names
            geography: Geography filter
        
        Returns:
            Dictionary containing series data
        """
        return self.execute_query(dataset, variables, geography, year=year)
    
    def get_timeseries(
        self,
        dataset: str,
        variables: List[str],
        time_range: Optional[Dict[str, str]] = None,
        geography: str = "us:1"
    ) -> Dict[str, Any]:
        """
        Get timeseries Census data.
        
        Args:
            dataset: Timeseries dataset identifier
            variables: List of variable names
            time_range: Dict with 'start' and 'end' dates (YYYY-MM-DD)
            geography: Geography filter
        
        Returns:
            Dictionary containing series data
        """
        return self.execute_query(dataset, variables, geography, time_range=time_range)
    
    def validate_variable(self, variable: str) -> Tuple[bool, Optional[str]]:
        """
        Validate variable name format.
        Returns (is_valid, error_message).
        """
        if not variable or not variable.strip():
            return False, "Variable name cannot be empty"
        
        if not validate_variable_format(variable):
            return False, f"Invalid variable format: {variable}. Variables should be uppercase alphanumeric with underscores (e.g., EMPSALUS, B01001_001E)"
        
        return True, None
    
    def get_suggestions(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[str]:
        """
        Get variable name suggestions based on query.
        """
        return search_census_variables(query, category=category, limit=limit)
    
    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search is limited for Census Bureau API.
        The Census Bureau API doesn't have a general search endpoint.
        Returns a message indicating manual lookup is required.
        """
        return {
            "query": search_text,
            "results": [],
            "count": 0,
            "message": "Census Bureau API does not support programmatic search. Please use specific variable names from Census datasets. You can browse available datasets at https://www.census.gov/data/developers/data-sets.html"
        }
    
    # Keep old get_series method for backward compatibility (deprecated)
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dataset: str = "timeseries/eits/mid",
        **kwargs
    ) -> Dict[str, Any]:
        """
        DEPRECATED: Use execute_query() instead.
        
        Get time series data from U.S. Census Bureau.
        """
        time_range = None
        if start_date or end_date:
            time_range = {}
            if start_date:
                time_range["start"] = start_date
            if end_date:
                time_range["end"] = end_date
        
        result = self.execute_query(
            dataset=dataset,
            variables=[series_id],
            geography="us:1",
            time_range=time_range
        )
        
        # Convert to old format for backward compatibility
        if result.get("data"):
            data_points = []
            for row in result["data"]:
                time_str = row.get("time", "")
                value_str = row.get(series_id, "")
                
                if time_str and value_str:
                    try:
                        value = float(value_str)
                        date_str = self._parse_census_date(time_str)
                        data_points.append({"date": date_str, "value": value})
                    except (ValueError, TypeError):
                        pass
            
            data_points.sort(key=lambda x: x['date'])
            
            return {
                "series_id": series_id,
                "title": f"Census Bureau: {series_id}",
                "units": "",
                "frequency": "Monthly" if dataset.startswith("timeseries") else "Annual",
                "seasonal_adjustment": "Not Seasonally Adjusted",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]['date'] if data_points else "",
                "observation_end": data_points[-1]['date'] if data_points else "",
                "data": data_points,
                "data_points": len(data_points)
            }
        
        return {
            "series_id": series_id,
            "title": f"Census Bureau: {series_id}",
            "units": "",
            "frequency": "Monthly",
            "seasonal_adjustment": "Not Seasonally Adjusted",
            "last_updated": datetime.now().isoformat(),
            "observation_start": "",
            "observation_end": "",
            "data": [],
            "data_points": 0
        }


# Global service instance (lazy initialization)
_census_service: Optional[CensusService] = None


def get_census_service() -> CensusService:
    """Get or create Census service instance."""
    global _census_service
    if _census_service is None:
        _census_service = CensusService()
    return _census_service

