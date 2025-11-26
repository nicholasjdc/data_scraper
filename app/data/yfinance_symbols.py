"""
Popular Yahoo Finance ticker symbols for autocomplete and validation.
Includes stocks, indices, and ETFs.
"""
from typing import List

# Major Market Indices
INDICES = [
    "^GSPC",  # S&P 500
    "^DJI",   # Dow Jones Industrial Average
    "^IXIC",  # NASDAQ Composite
    "^RUT",   # Russell 2000
    "^VIX",   # CBOE Volatility Index
    "^TNX",   # 10-Year Treasury Note
    "^FVX",   # 5-Year Treasury Note
    "^IRX",   # 13 Week Treasury Bill
]

# Popular ETFs
ETFS = [
    "SPY",    # SPDR S&P 500 ETF
    "QQQ",    # Invesco QQQ Trust
    "DIA",    # SPDR Dow Jones Industrial Average ETF
    "IWM",    # iShares Russell 2000 ETF
    "VTI",    # Vanguard Total Stock Market ETF
    "VOO",    # Vanguard S&P 500 ETF
    "VEA",    # Vanguard FTSE Developed Markets ETF
    "VWO",    # Vanguard FTSE Emerging Markets ETF
    "BND",    # Vanguard Total Bond Market ETF
    "GLD",    # SPDR Gold Trust
    "SLV",    # iShares Silver Trust
    "USO",    # United States Oil Fund
    "TLT",    # iShares 20+ Year Treasury Bond ETF
    "HYG",    # iShares iBoxx $ High Yield Corporate Bond ETF
    "EFA",    # iShares MSCI EAFE ETF
    "EEM",    # iShares MSCI Emerging Markets ETF
]

# Dow 30 Components
DOW_30 = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "UNH",    # UnitedHealth Group
    "GS",     # Goldman Sachs
    "HD",     # Home Depot
    "CAT",    # Caterpillar
    "MCD",    # McDonald's
    "V",      # Visa
    "HON",    # Honeywell
    "TRV",    # Travelers
    "AXP",    # American Express
    "AMGN",   # Amgen
    "JPM",    # JPMorgan Chase
    "CVX",    # Chevron
    "WMT",    # Walmart
    "MRK",    # Merck
    "PG",     # Procter & Gamble
    "BA",     # Boeing
    "DIS",    # Disney
    "DOW",    # Dow Inc
    "IBM",    # IBM
    "AMZN",   # Amazon
    "CRM",    # Salesforce
    "NKE",    # Nike
    "JNJ",    # Johnson & Johnson
    "CSCO",   # Cisco
    "VZ",     # Verizon
    "INTC",   # Intel
    "WBA",    # Walgreens Boots Alliance
]

# Top S&P 500 Stocks (Most Popular)
SP500_TOP = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet Class A
    "GOOG",   # Alphabet Class C
    "AMZN",   # Amazon
    "NVDA",   # NVIDIA
    "META",   # Meta Platforms
    "TSLA",   # Tesla
    "BRK.B",  # Berkshire Hathaway Class B
    "UNH",    # UnitedHealth Group
    "XOM",    # Exxon Mobil
    "JNJ",    # Johnson & Johnson
    "JPM",    # JPMorgan Chase
    "V",      # Visa
    "PG",     # Procter & Gamble
    "MA",     # Mastercard
    "CVX",    # Chevron
    "HD",     # Home Depot
    "ABBV",   # AbbVie
    "PFE",    # Pfizer
    "AVGO",   # Broadcom
    "COST",   # Costco
    "MRK",    # Merck
    "WMT",    # Walmart
    "PEP",    # PepsiCo
    "TMO",    # Thermo Fisher Scientific
    "CSCO",   # Cisco
    "ABT",    # Abbott Laboratories
    "ACN",    # Accenture
    "ADBE",   # Adobe
    "NFLX",   # Netflix
    "NKE",    # Nike
    "DHR",    # Danaher
    "VZ",     # Verizon
    "TXN",    # Texas Instruments
    "CMCSA",  # Comcast
    "NEE",    # NextEra Energy
    "PM",     # Philip Morris
    "LIN",    # Linde
    "DIS",    # Disney
    "RTX",    # Raytheon Technologies
    "HON",    # Honeywell
    "QCOM",   # Qualcomm
    "AMGN",   # Amgen
    "AMT",    # American Tower
    "INTU",   # Intuit
    "IBM",    # IBM
    "UNP",    # Union Pacific
    "LOW",    # Lowe's
    "SPGI",   # S&P Global
    "AXP",    # American Express
    "GE",     # General Electric
    "BKNG",   # Booking Holdings
    "PLD",    # Prologis
    "AMAT",   # Applied Materials
    "DE",     # Deere & Company
    "ADI",    # Analog Devices
    "SBUX",   # Starbucks
    "GILD",   # Gilead Sciences
    "MDT",    # Medtronic
    "ISRG",   # Intuitive Surgical
    "ADP",    # Automatic Data Processing
    "C",      # Citigroup
    "VRTX",   # Vertex Pharmaceuticals
    "TJX",    # TJX Companies
    "ZTS",    # Zoetis
    "REGN",   # Regeneron Pharmaceuticals
    "MMC",    # Marsh & McLennan
    "LMT",    # Lockheed Martin
    "ETN",    # Eaton
    "PANW",   # Palo Alto Networks
    "FI",     # Fiserv
    "CDNS",   # Cadence Design Systems
    "KLAC",   # KLA Corporation
    "SNPS",   # Synopsys
    "APH",    # Amphenol
    "SHW",    # Sherwin-Williams
    "MCO",    # Moody's
    "ICE",    # Intercontinental Exchange
    "EQIX",   # Equinix
    "CRWD",   # CrowdStrike
    "FTNT",   # Fortinet
    "CTSH",   # Cognizant
    "NXPI",   # NXP Semiconductors
    "CDW",    # CDW Corporation
    "FAST",   # Fastenal
    "PAYX",   # Paychex
    "ANET",   # Arista Networks
    "PCAR",   # PACCAR
    "ODFL",   # Old Dominion Freight Line
    "CTAS",   # Cintas
    "KEYS",   # Keysight Technologies
    "IDXX",   # IDEXX Laboratories
    "MCHP",   # Microchip Technology
    "ON",     # ON Semiconductor
    "DXCM",   # Dexcom
    "TTD",    # The Trade Desk
    "FDS",    # FactSet
    "NDAQ",   # Nasdaq
    "EXPD",   # Expeditors International
    "WDAY",   # Workday
    "CPRT",   # Copart
    "VRSN",   # VeriSign
    "FTV",    # Fortive
    "MPWR",   # Monolithic Power Systems
    "INCY",   # Incyte
    "CHTR",   # Charter Communications
    "ALGN",   # Align Technology
    "TEAM",   # Atlassian
    "ZS",     # Zscaler
    "DOCN",   # DigitalOcean
    "DOCU",   # DocuSign
]

# Popular NASDAQ Stocks
NASDAQ_POPULAR = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet
    "GOOG",   # Alphabet Class C
    "AMZN",   # Amazon
    "NVDA",   # NVIDIA
    "META",   # Meta Platforms
    "TSLA",   # Tesla
    "AVGO",   # Broadcom
    "COST",   # Costco
    "NFLX",   # Netflix
    "ADBE",   # Adobe
    "PEP",    # PepsiCo
    "CSCO",   # Cisco
    "CMCSA",  # Comcast
    "TXN",    # Texas Instruments
    "QCOM",   # Qualcomm
    "INTU",   # Intuit
    "AMGN",   # Amgen
    "ISRG",   # Intuitive Surgical
    "AMD",    # Advanced Micro Devices
    "INTC",   # Intel
    "AMAT",   # Applied Materials
    "MU",     # Micron Technology
    "LRCX",   # Lam Research
    "KLAC",   # KLA Corporation
    "MCHP",   # Microchip Technology
    "NXPI",   # NXP Semiconductors
    "SWKS",   # Skyworks Solutions
    "QRVO",   # Qorvo
    "MRVL",   # Marvell Technology
    "CRWD",   # CrowdStrike
    "FTNT",   # Fortinet
    "ZS",     # Zscaler
    "PANW",   # Palo Alto Networks
    "OKTA",   # Okta
    "ZM",     # Zoom
    "DOCU",   # DocuSign
    "TEAM",   # Atlassian
    "WDAY",   # Workday
    "SNOW",   # Snowflake
    "DDOG",   # Datadog
    "NET",    # Cloudflare
    "MDB",    # MongoDB
    "ESTC",   # Elastic
    "SPLK",   # Splunk
    "NOW",    # ServiceNow
    "CRM",    # Salesforce
    "ORCL",   # Oracle
    "ADSK",   # Autodesk
    "ANSS",   # ANSYS
    "CDNS",   # Cadence Design Systems
    "SNPS",   # Synopsys
    "KEYS",   # Keysight Technologies
    "TTWO",   # Take-Two Interactive
    "EA",     # Electronic Arts
    "ATVI",   # Activision Blizzard
    "RBLX",   # Roblox
    "U",      # Unity Software
    "HOOD",   # Robinhood
    "COIN",   # Coinbase
    "SQ",     # Block
    "PYPL",   # PayPal
    "AFRM",   # Affirm
    "UPST",   # Upstart
    "SOFI",   # SoFi Technologies
    "LCID",   # Lucid Group
    "RIVN",   # Rivian Automotive
    "F",      # Ford
    "GM",     # General Motors
    "LCID",   # Lucid
    "NIO",    # NIO
    "XPEV",   # XPeng
    "LI",     # Li Auto
    "BIDU",   # Baidu
    "JD",     # JD.com
    "PDD",    # PDD Holdings
    "BABA",   # Alibaba
    "TME",    # Tencent Music
    "NTES",   # NetEase
]

# Combine all symbols
ALL_SYMBOLS = sorted(set(INDICES + ETFS + DOW_30 + SP500_TOP + NASDAQ_POPULAR))

# Categorize symbols for autocomplete
SYMBOL_CATEGORIES = {
    "indices": INDICES,
    "etfs": ETFS,
    "dow_30": DOW_30,
    "sp500": SP500_TOP,
    "nasdaq": NASDAQ_POPULAR,
}

def get_symbols_by_category(category: str = None):
    """Get symbols filtered by category."""
    if category and category in SYMBOL_CATEGORIES:
        return SYMBOL_CATEGORIES[category]
    return ALL_SYMBOLS

def validate_symbol_format(symbol: str) -> bool:
    """
    Validate Yahoo Finance symbol format.
    Valid formats: uppercase alphanumeric, can start with ^ for indices.
    """
    if not symbol or len(symbol) == 0:
        return False
    
    # Remove leading ^ for indices
    clean_symbol = symbol.lstrip('^')
    
    # Must be alphanumeric, 1-5 characters typically
    if not clean_symbol.isalnum() or len(clean_symbol) < 1 or len(clean_symbol) > 10:
        return False
    
    return True

def search_symbols(query: str, limit: int = 20) -> List[str]:
    """
    Search symbols matching query (case-insensitive).
    Returns list of matching symbols.
    """
    if not query:
        return ALL_SYMBOLS[:limit]
    
    query_upper = query.upper()
    matches = [s for s in ALL_SYMBOLS if query_upper in s.upper()]
    return matches[:limit]

