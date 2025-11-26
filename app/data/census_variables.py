"""
Common U.S. Census Bureau variable names for autocomplete and validation.
Organized by dataset/category.
"""
from typing import List

# Economic Indicators Time Series (timeseries/eits/mid)
ECONOMIC_INDICATORS = [
    "EMPSAL",      # Employment and Salaries
    "EMPSALUS",    # Employment and Salaries - United States
    "EMPSALUSM",   # Employment and Salaries - United States - Monthly
    "EMPSALUSQ",   # Employment and Salaries - United States - Quarterly
    "EMPSALUSY",   # Employment and Salaries - United States - Yearly
    "EMPSALUSMNSA", # Employment and Salaries - United States - Monthly - Not Seasonally Adjusted
    "EMPSALUSQNSA", # Employment and Salaries - United States - Quarterly - Not Seasonally Adjusted
    "EMPSALUSYNSA", # Employment and Salaries - United States - Yearly - Not Seasonally Adjusted
    "EMPSALUSMSA",  # Employment and Salaries - United States - Monthly - Seasonally Adjusted
    "EMPSALUSQSA",  # Employment and Salaries - United States - Quarterly - Seasonally Adjusted
    "EMPSALUSYSA",  # Employment and Salaries - United States - Yearly - Seasonally Adjusted
    "EMPSALUSMCH",  # Employment and Salaries - United States - Monthly - Change
    "EMPSALUSQCH",  # Employment and Salaries - United States - Quarterly - Change
    "EMPSALUSYCH",  # Employment and Salaries - United States - Yearly - Change
    "EMPSALUSMPCH", # Employment and Salaries - United States - Monthly - Percent Change
    "EMPSALUSQPCH", # Employment and Salaries - United States - Quarterly - Percent Change
    "EMPSALUSYPCH", # Employment and Salaries - United States - Yearly - Percent Change
    "EMPSALUSMCHNSA", # Employment and Salaries - United States - Monthly - Change - Not Seasonally Adjusted
    "EMPSALUSQCHNSA", # Employment and Salaries - United States - Quarterly - Change - Not Seasonally Adjusted
    "EMPSALUSYCHNSA", # Employment and Salaries - United States - Yearly - Change - Not Seasonally Adjusted
    "EMPSALUSMPCHNSA", # Employment and Salaries - United States - Monthly - Percent Change - Not Seasonally Adjusted
    "EMPSALUSQPCHNSA", # Employment and Salaries - United States - Quarterly - Percent Change - Not Seasonally Adjusted
    "EMPSALUSYPCHNSA", # Employment and Salaries - United States - Yearly - Percent Change - Not Seasonally Adjusted
    "EMPSALUSMCHSA",  # Employment and Salaries - United States - Monthly - Change - Seasonally Adjusted
    "EMPSALUSQCHSA",  # Employment and Salaries - United States - Quarterly - Change - Seasonally Adjusted
    "EMPSALUSYCHSA",  # Employment and Salaries - United States - Yearly - Change - Seasonally Adjusted
    "EMPSALUSMPCHSA", # Employment and Salaries - United States - Monthly - Percent Change - Seasonally Adjusted
    "EMPSALUSQPCHSA", # Employment and Salaries - United States - Quarterly - Percent Change - Seasonally Adjusted
    "EMPSALUSYPCHSA", # Employment and Salaries - United States - Yearly - Percent Change - Seasonally Adjusted
]

# Retail Trade (timeseries/eits/retail)
RETAIL_TRADE = [
    "RETAIL",      # Retail Trade
    "RETAILUS",    # Retail Trade - United States
    "RETAILUSM",   # Retail Trade - United States - Monthly
    "RETAILUSQ",   # Retail Trade - United States - Quarterly
    "RETAILUSY",   # Retail Trade - United States - Yearly
    "RETAILUSMNSA", # Retail Trade - United States - Monthly - Not Seasonally Adjusted
    "RETAILUSQNSA", # Retail Trade - United States - Quarterly - Not Seasonally Adjusted
    "RETAILUSYNSA", # Retail Trade - United States - Yearly - Not Seasonally Adjusted
    "RETAILUSMSA",  # Retail Trade - United States - Monthly - Seasonally Adjusted
    "RETAILUSQSA",  # Retail Trade - United States - Quarterly - Seasonally Adjusted
    "RETAILUSYSA",  # Retail Trade - United States - Yearly - Seasonally Adjusted
]

# Manufacturing (timeseries/eits/manufacturing)
MANUFACTURING = [
    "MANUF",       # Manufacturing
    "MANUFUS",     # Manufacturing - United States
    "MANUFUSM",    # Manufacturing - United States - Monthly
    "MANUFUSQ",    # Manufacturing - United States - Quarterly
    "MANUFUSY",    # Manufacturing - United States - Yearly
    "MANUFUSMNSA", # Manufacturing - United States - Monthly - Not Seasonally Adjusted
    "MANUFUSQNSA", # Manufacturing - United States - Quarterly - Not Seasonally Adjusted
    "MANUFUSYNSA", # Manufacturing - United States - Yearly - Not Seasonally Adjusted
    "MANUFUSMSA",  # Manufacturing - United States - Monthly - Seasonally Adjusted
    "MANUFUSQSA",  # Manufacturing - United States - Quarterly - Seasonally Adjusted
    "MANUFUSYSA",  # Manufacturing - United States - Yearly - Seasonally Adjusted
]

# Construction (timeseries/eits/construction)
CONSTRUCTION = [
    "CONST",       # Construction
    "CONSTUS",     # Construction - United States
    "CONSTUSM",    # Construction - United States - Monthly
    "CONSTUSQ",    # Construction - United States - Quarterly
    "CONSTUSY",    # Construction - United States - Yearly
    "CONSTUSMNSA", # Construction - United States - Monthly - Not Seasonally Adjusted
    "CONSTUSQNSA", # Construction - United States - Quarterly - Not Seasonally Adjusted
    "CONSTUSYNSA", # Construction - United States - Yearly - Not Seasonally Adjusted
    "CONSTUSMSA",  # Construction - United States - Monthly - Seasonally Adjusted
    "CONSTUSQSA",  # Construction - United States - Quarterly - Seasonally Adjusted
    "CONSTUSYSA",  # Construction - United States - Yearly - Seasonally Adjusted
]

# Wholesale Trade (timeseries/eits/wholesale)
WHOLESALE = [
    "WHOLESALE",   # Wholesale Trade
    "WHOLESALEUS", # Wholesale Trade - United States
    "WHOLESALEUSM", # Wholesale Trade - United States - Monthly
    "WHOLESALEUSQ", # Wholesale Trade - United States - Quarterly
    "WHOLESALEUSY", # Wholesale Trade - United States - Yearly
]

# Common ACS (American Community Survey) Variables
ACS_VARIABLES = [
    "B01001_001E",  # Total Population
    "B19013_001E",  # Median Household Income
    "B25064_001E",  # Median Gross Rent
    "B25077_001E",  # Median Home Value
    "B08301_001E",  # Means of Transportation to Work
    "B15003_001E",  # Educational Attainment
    "B17001_001E",  # Poverty Status
    "B25001_001E",  # Total Housing Units
    "B25002_001E",  # Occupancy Status
    "B25003_001E",  # Tenure
]

# Common Economic Census Variables
ECONOMIC_CENSUS = [
    "NAICS2012",   # NAICS Code
    "NAICS2017",   # NAICS Code (2017)
    "GEO_ID",      # Geographic Identifier
    "NAME",        # Name
    "YEAR",        # Year
    "ESTAB",       # Establishments
    "EMP",         # Employment
    "PAYANN",      # Annual Payroll
    "RCPTOT",      # Total Receipts
]

# Combine all variables
ALL_VARIABLES = sorted(set(
    ECONOMIC_INDICATORS + 
    RETAIL_TRADE + 
    MANUFACTURING + 
    CONSTRUCTION + 
    WHOLESALE + 
    ACS_VARIABLES + 
    ECONOMIC_CENSUS
))

# Categorize variables
VARIABLE_CATEGORIES = {
    "economic_indicators": ECONOMIC_INDICATORS,
    "retail_trade": RETAIL_TRADE,
    "manufacturing": MANUFACTURING,
    "construction": CONSTRUCTION,
    "wholesale": WHOLESALE,
    "acs": ACS_VARIABLES,
    "economic_census": ECONOMIC_CENSUS,
}

def get_variables_by_category(category: str = None):
    """Get variables filtered by category."""
    if category and category in VARIABLE_CATEGORIES:
        return VARIABLE_CATEGORIES[category]
    return ALL_VARIABLES

def validate_variable_format(variable: str) -> bool:
    """
    Validate Census Bureau variable name format.
    Valid formats: uppercase alphanumeric with underscores, typically 5-20 characters.
    """
    if not variable or len(variable) == 0:
        return False
    
    variable_upper = variable.upper()
    
    # Must be alphanumeric or underscore, typically 3-50 characters
    if not all(c.isalnum() or c == '_' for c in variable_upper):
        return False
    
    if len(variable_upper) < 3 or len(variable_upper) > 50:
        return False
    
    return True

def search_variables(query: str, category: str = None, limit: int = 20) -> List[str]:
    """
    Search variables matching query (case-insensitive).
    Returns list of matching variable names.
    """
    if not query:
        variables = get_variables_by_category(category)
        return variables[:limit]
    
    query_upper = query.upper()
    variables = get_variables_by_category(category)
    matches = [v for v in variables if query_upper in v.upper()]
    return matches[:limit]

