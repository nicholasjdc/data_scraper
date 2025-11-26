"""
Popular Alpha Vantage symbols for autocomplete and validation.
Includes stocks, forex pairs, and cryptocurrencies.
"""
from typing import Tuple, List

# Popular Stocks (S&P 500 top stocks)
STOCKS = [
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
]

# Major Forex Pairs
FOREX_PAIRS = [
    "EUR/USD",  # Euro / US Dollar
    "GBP/USD",  # British Pound / US Dollar
    "USD/JPY",  # US Dollar / Japanese Yen
    "USD/CHF",  # US Dollar / Swiss Franc
    "AUD/USD",  # Australian Dollar / US Dollar
    "USD/CAD",  # US Dollar / Canadian Dollar
    "NZD/USD",  # New Zealand Dollar / US Dollar
    "EUR/GBP",  # Euro / British Pound
    "EUR/JPY",  # Euro / Japanese Yen
    "GBP/JPY",  # British Pound / Japanese Yen
    "EUR/CHF",  # Euro / Swiss Franc
    "AUD/JPY",  # Australian Dollar / Japanese Yen
    "EUR/AUD",  # Euro / Australian Dollar
    "GBP/AUD",  # British Pound / Australian Dollar
    "USD/CNH",  # US Dollar / Chinese Yuan
    "USD/HKD",  # US Dollar / Hong Kong Dollar
    "USD/SGD",  # US Dollar / Singapore Dollar
    "USD/ZAR",  # US Dollar / South African Rand
    "USD/MXN",  # US Dollar / Mexican Peso
    "USD/BRL",  # US Dollar / Brazilian Real
    "USD/INR",  # US Dollar / Indian Rupee
    "USD/KRW",  # US Dollar / South Korean Won
    "USD/TRY",  # US Dollar / Turkish Lira
    "USD/RUB",  # US Dollar / Russian Ruble
    "EUR/CAD",  # Euro / Canadian Dollar
    "GBP/CAD",  # British Pound / Canadian Dollar
    "AUD/CAD",  # Australian Dollar / Canadian Dollar
    "EUR/NZD",  # Euro / New Zealand Dollar
    "GBP/NZD",  # British Pound / New Zealand Dollar
    "AUD/NZD",  # Australian Dollar / New Zealand Dollar
    "CHF/JPY",  # Swiss Franc / Japanese Yen
    "CAD/JPY",  # Canadian Dollar / Japanese Yen
    "NZD/JPY",  # New Zealand Dollar / Japanese Yen
    "EUR/SEK",  # Euro / Swedish Krona
    "EUR/NOK",  # Euro / Norwegian Krone
    "EUR/DKK",  # Euro / Danish Krone
    "EUR/PLN",  # Euro / Polish Zloty
    "EUR/CZK",  # Euro / Czech Koruna
    "GBP/CHF",  # British Pound / Swiss Franc
    "AUD/CHF",  # Australian Dollar / Swiss Franc
    "CAD/CHF",  # Canadian Dollar / Swiss Franc
]

# Major Cryptocurrencies
CRYPTO = [
    "BTC",     # Bitcoin
    "ETH",     # Ethereum
    "BNB",     # Binance Coin
    "SOL",     # Solana
    "XRP",     # Ripple
    "ADA",     # Cardano
    "DOGE",    # Dogecoin
    "DOT",     # Polkadot
    "MATIC",   # Polygon
    "AVAX",    # Avalanche
    "LINK",    # Chainlink
    "UNI",     # Uniswap
    "LTC",     # Litecoin
    "ATOM",    # Cosmos
    "ETC",     # Ethereum Classic
    "XLM",     # Stellar
    "ALGO",    # Algorand
    "VET",     # VeChain
    "ICP",     # Internet Computer
    "FIL",     # Filecoin
    "TRX",     # TRON
    "EOS",     # EOS
    "AAVE",    # Aave
    "MKR",     # Maker
    "COMP",    # Compound
    "SUSHI",   # SushiSwap
    "CRV",     # Curve
    "YFI",     # Yearn Finance
    "SNX",     # Synthetix
    "1INCH",   # 1inch
]

# Combine all symbols
ALL_STOCKS = sorted(set(STOCKS))
ALL_FOREX = sorted(FOREX_PAIRS)
ALL_CRYPTO = sorted(set(CRYPTO))

# All symbols for general search
ALL_SYMBOLS = ALL_STOCKS + ALL_FOREX + ALL_CRYPTO

# Categorize symbols
SYMBOL_CATEGORIES = {
    "stocks": ALL_STOCKS,
    "forex": ALL_FOREX,
    "crypto": ALL_CRYPTO,
}

def get_symbols_by_category(category: str = None):
    """Get symbols filtered by category."""
    if category and category in SYMBOL_CATEGORIES:
        return SYMBOL_CATEGORIES[category]
    return ALL_SYMBOLS

def validate_symbol_format(symbol: str) -> Tuple[bool, str]:
    """
    Validate Alpha Vantage symbol format.
    Returns (is_valid, symbol_type).
    Types: 'stock', 'forex', 'crypto', 'invalid'
    """
    if not symbol or len(symbol) == 0:
        return False, "invalid"
    
    symbol_upper = symbol.upper()
    
    # Check if forex pair (XXX/YYY format)
    if '/' in symbol_upper:
        parts = symbol_upper.split('/')
        if len(parts) == 2:
            # Both parts should be 3-letter currency codes
            if len(parts[0]) == 3 and len(parts[1]) == 3 and parts[0].isalpha() and parts[1].isalpha():
                return True, "forex"
        return False, "invalid"
    
    # Check if crypto (typically 3-5 uppercase letters)
    if symbol_upper in ALL_CRYPTO:
        return True, "crypto"
    
    # Check if stock (alphanumeric, 1-5 characters typically, may have .)
    if symbol_upper.replace('.', '').isalnum() and 1 <= len(symbol_upper) <= 10:
        # Could be a stock - allow it (soft validation)
        return True, "stock"
    
    return False, "invalid"

def search_symbols(query: str, category: str = None, limit: int = 20) -> List[Tuple[str, str]]:
    """
    Search symbols matching query (case-insensitive).
    Returns list of matching symbols with type information.
    """
    if not query:
        symbols = get_symbols_by_category(category)
        return [(s, _get_symbol_type(s)) for s in symbols[:limit]]
    
    query_upper = query.upper()
    results = []
    
    # Search in appropriate category
    search_list = get_symbols_by_category(category)
    
    for symbol in search_list:
        if query_upper in symbol.upper():
            symbol_type = _get_symbol_type(symbol)
            results.append((symbol, symbol_type))
            if len(results) >= limit:
                break
    
    return results

def _get_symbol_type(symbol: str) -> str:
    """Determine symbol type."""
    if '/' in symbol:
        return "forex"
    elif symbol.upper() in ALL_CRYPTO:
        return "crypto"
    else:
        return "stock"

