"""
Real Census Bureau variable names for autocomplete and validation.

For EITS (Economic Indicators Time Series) datasets the API is multi-dimensional:
  you request CELL_VALUE and filter by dimension codes (CATEGORY_CODE, NAICS, etc.)
  rather than using a single composite variable ID.

For ACS (American Community Survey) datasets you request table variables like
  B01001_001E directly.

See https://www.census.gov/data/developers/data-sets.html for dataset documentation.
"""
from typing import List

# ── EITS query variables (timeseries/eits/* datasets) ─────────────────────────
# These are the actual column names accepted by all EITS endpoints.
# Always include CELL_VALUE in your variables list; add dimension columns to
# control what you get back, and use filters (e.g. CATEGORY_CODE=RSA) as params.

EITS_COMMON = [
    "CELL_VALUE",      # The numeric data value (always required)
    "CATEGORY_CODE",   # Data category filter (e.g. RSA, EMP, SAL)
    "DATA_TYPE_CODE",  # Level (L), percent change (P), etc.
    "GEO_LEVEL_CODE",  # N=national, R=region, S=state
    "GEO_CODE",        # Geography identifier
    "GEO_NAME",        # Geography label
    "YEAR",            # 4-digit year
    "MONTH",           # 2-digit month (01–12)
    "PERIOD_TYPE",     # M=monthly, Q=quarterly
    "ERROR_DATA",      # Margin of error
]

# timeseries/eits/mid — Monthly Industry Data (employment, hours, earnings)
EITS_MID = [
    "CELL_VALUE",
    "CATEGORY_CODE",   # EMP (employment), SAL (salaries), HRS (hours)
    "DATA_TYPE_CODE",
    "GEO_LEVEL_CODE",
    "IND_LEVEL_CODE",  # Industry level
    "IND_CODE",        # Industry code
    "IND_NAME",        # Industry label
    "YEAR",
    "MONTH",
]

# timeseries/eits/retail — Monthly Retail Trade and Food Services
EITS_RETAIL = [
    "CELL_VALUE",
    "CATEGORY_CODE",   # RSA (retail sales adjusted), RCA (retail change adjusted)
    "DATA_TYPE_CODE",
    "GEO_LEVEL_CODE",
    "NAICS",           # NAICS industry code
    "YEAR",
    "MONTH",
    "ERROR_DATA",
]

# timeseries/eits/manufacturing — Manufacturing and Trade Inventories and Sales
EITS_MFGM = [
    "CELL_VALUE",
    "CATEGORY_CODE",   # SMV (sales, manufacturers), IVM (inventories, manufacturers)
    "DATA_TYPE_CODE",
    "GEO_LEVEL_CODE",
    "TYPE_CODE",       # Industry classification
    "YEAR",
    "MONTH",
]

# timeseries/eits/cbh — Construction Spending
EITS_CONSTRUCTION = [
    "CELL_VALUE",
    "CATEGORY_CODE",   # PRIV (private), PUB (public), TOT (total)
    "TYPE_CODE",
    "GEO_LEVEL_CODE",
    "YEAR",
    "MONTH",
]

# timeseries/eits/wholesale — Monthly Wholesale Trade
EITS_WHOLESALE = [
    "CELL_VALUE",
    "CATEGORY_CODE",
    "DATA_TYPE_CODE",
    "NAICS",
    "YEAR",
    "MONTH",
]

# ── ACS (American Community Survey) variables ──────────────────────────────────
# These are real ACS 5-year estimate variable codes.
# Source: https://api.census.gov/data/2022/acs/acs5/variables.json
ACS_VARIABLES = [
    # Population
    "B01001_001E",  # Total population
    "B01002_001E",  # Median age (total)
    "B01002_002E",  # Median age (male)
    "B01002_003E",  # Median age (female)

    # Income
    "B19013_001E",  # Median household income (past 12 months, inflation-adjusted)
    "B19025_001E",  # Aggregate household income
    "B19083_001E",  # Gini index of income inequality

    # Poverty
    "B17001_002E",  # Population below poverty level
    "B17001_001E",  # Total population for poverty determination

    # Housing
    "B25001_001E",  # Total housing units
    "B25002_002E",  # Occupied housing units
    "B25003_002E",  # Owner-occupied units
    "B25003_003E",  # Renter-occupied units
    "B25064_001E",  # Median gross rent
    "B25077_001E",  # Median home value (owner-occupied units)

    # Education
    "B15003_017E",  # High school graduate
    "B15003_022E",  # Bachelor's degree
    "B15003_023E",  # Master's degree
    "B15003_025E",  # Doctorate degree

    # Commuting
    "B08301_001E",  # Total workers 16+ commuting
    "B08301_010E",  # Worked from home
    "B08303_001E",  # Travel time to work total
]

# ── Economic Census variables ──────────────────────────────────────────────────
# Used with year-based datasets like ecnbasic, ecnsize, etc.
ECONOMIC_CENSUS = [
    "NAICS2017",    # NAICS 2017 code
    "GEO_ID",       # Geographic identifier
    "NAME",         # Geography/industry name
    "YEAR",         # Reference year
    "ESTAB",        # Number of establishments
    "EMP",          # Employment (paid employees)
    "PAYANN",       # Annual payroll ($1,000)
    "RCPTOT",       # Total receipts/revenue ($1,000)
    "FIRMPDEMP",    # Firms (partnership / non-employer)
]

# Population Estimates Program
PEP_VARIABLES = [
    "POP",          # Resident population
    "DENSITY",      # Population density per square mile
    "BIRTHS",       # Births
    "DEATHS",       # Deaths
    "NATURALINC",   # Natural increase (births minus deaths)
    "INTERNATIONALMIG",  # Net international migration
    "DOMESTICMIG",  # Net domestic migration
    "NETMIG",       # Net migration (domestic + international)
]

# ── Combined list for autocomplete ────────────────────────────────────────────
ALL_VARIABLES = sorted(set(
    EITS_COMMON
    + EITS_MID
    + EITS_RETAIL
    + EITS_MFGM
    + EITS_CONSTRUCTION
    + EITS_WHOLESALE
    + ACS_VARIABLES
    + ECONOMIC_CENSUS
    + PEP_VARIABLES
))

VARIABLE_CATEGORIES = {
    "eits_common": EITS_COMMON,
    "eits_mid": EITS_MID,
    "eits_retail": EITS_RETAIL,
    "eits_manufacturing": EITS_MFGM,
    "eits_construction": EITS_CONSTRUCTION,
    "eits_wholesale": EITS_WHOLESALE,
    "acs": ACS_VARIABLES,
    "economic_census": ECONOMIC_CENSUS,
    "pep": PEP_VARIABLES,
}


def get_variables_by_category(category: str = None) -> List[str]:
    if category and category in VARIABLE_CATEGORIES:
        return VARIABLE_CATEGORIES[category]
    return ALL_VARIABLES


def validate_variable_format(variable: str) -> bool:
    if not variable:
        return False
    v = variable.upper()
    if not all(c.isalnum() or c == '_' for c in v):
        return False
    return 2 <= len(v) <= 50


def search_variables(query: str, category: str = None, limit: int = 20) -> List[str]:
    variables = get_variables_by_category(category)
    if not query:
        return variables[:limit]
    q = query.upper()
    return [v for v in variables if q in v][:limit]
