"""
SEC EDGAR service — company fundamentals from XBRL filings.

Series ID format:  TICKER:CONCEPT
  e.g.  AAPL:Revenues
        MSFT:NetIncomeLoss
        TSLA:EarningsPerShareBasic

The concept is a US-GAAP or IFRS-FULL tag name (case-sensitive).
Common concepts are listed in EDGAR_CONCEPTS below.

Data is sourced from SEC EDGAR company facts:
  https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit}.json

Rate limit: 10 requests/second per SEC fair-use policy.
No API key required; User-Agent header is required.
"""
import re
import time
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple

import requests
from fastapi import HTTPException


EDGAR_CONCEPTS = [
    # Income statement
    ("Revenues", "Total revenues"),
    ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenue (ASC 606)"),
    ("NetIncomeLoss", "Net income / (loss)"),
    ("OperatingIncomeLoss", "Operating income / (loss)"),
    ("GrossProfit", "Gross profit"),
    ("CostOfRevenue", "Cost of revenue"),
    ("ResearchAndDevelopmentExpense", "R&D expense"),
    ("SellingGeneralAndAdministrativeExpense", "SG&A expense"),
    ("EarningsPerShareBasic", "Basic EPS"),
    ("EarningsPerShareDiluted", "Diluted EPS"),
    # Balance sheet
    ("Assets", "Total assets"),
    ("Liabilities", "Total liabilities"),
    ("StockholdersEquity", "Stockholders equity"),
    ("CashAndCashEquivalentsAtCarryingValue", "Cash and equivalents"),
    ("LongTermDebt", "Long-term debt"),
    ("RetainedEarningsAccumulatedDeficit", "Retained earnings"),
    ("CommonStockSharesOutstanding", "Shares outstanding"),
    # Cash flow
    ("NetCashProvidedByUsedInOperatingActivities", "Operating cash flow"),
    ("NetCashProvidedByUsedInInvestingActivities", "Investing cash flow"),
    ("NetCashProvidedByUsedInFinancingActivities", "Financing cash flow"),
    ("CapitalExpenditureDiscontinuedOperations", "Capital expenditures"),
    ("PaymentsToAcquirePropertyPlantAndEquipment", "CapEx (PP&E purchases)"),
    ("DividendsCommonStock", "Common dividends paid"),
]

EDGAR_CONCEPTS_MAP = {c[0]: c[1] for c in EDGAR_CONCEPTS}

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
_HEADERS = {
    "User-Agent": "provenance-dashboard noreply@localhost",
    "Accept-Encoding": "gzip, deflate",
}

# Form types considered annual (use for default if available)
_ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "40-F"}
_QUARTERLY_FORMS = {"10-Q", "10-Q/A"}


@lru_cache(maxsize=1)
def _load_ticker_map() -> Dict[str, int]:
    """Fetch and cache the SEC company tickers JSON. Returns {TICKER: CIK}."""
    resp = requests.get(_TICKERS_URL, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    return {
        entry["ticker"].upper(): int(entry["cik_str"])
        for entry in raw.values()
    }


def _cik_for_ticker(ticker: str) -> int:
    m = _load_ticker_map()
    cik = m.get(ticker.upper())
    if cik is None:
        raise ValueError(
            f"Ticker '{ticker}' not found in SEC EDGAR. "
            "Check the ticker symbol or use the company's CIK directly."
        )
    return cik


def _fetch_company_facts(cik: int) -> Dict:
    url = _FACTS_URL.format(cik=str(cik).zfill(10))
    resp = requests.get(url, headers=_HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _extract_series(facts: Dict, concept: str) -> Tuple[List[Dict], str, str]:
    """
    Pull a time series for concept from company facts JSON.
    Returns (data_points, units_label, entity_name).
    Prefers annual (10-K) data; falls back to quarterly (10-Q).
    """
    entity = facts.get("entityName", "")

    for taxonomy in ("us-gaap", "ifrs-full", "dei"):
        tax_data = facts.get("facts", {}).get(taxonomy, {})
        if concept not in tax_data:
            continue
        concept_data = tax_data[concept]
        label = concept_data.get("label", concept)

        # Find the unit type (USD, shares, pure, etc.)
        units_dict = concept_data.get("units", {})
        if not units_dict:
            continue

        unit_key = next(iter(units_dict))
        filings = units_dict[unit_key]

        # Prefer annual periods; fall back to all periods
        annual = [
            f for f in filings
            if f.get("form") in _ANNUAL_FORMS and f.get("end") and f.get("val") is not None
        ]
        quarterly = [
            f for f in filings
            if f.get("form") in _QUARTERLY_FORMS and f.get("end") and f.get("val") is not None
        ]

        source = annual if annual else quarterly
        if not source:
            source = [f for f in filings if f.get("end") and f.get("val") is not None]

        # De-duplicate by end date (keep most recently filed for each date)
        by_date: Dict[str, Dict] = {}
        for f in source:
            end = f["end"]
            if end not in by_date or f["filed"] > by_date[end]["filed"]:
                by_date[end] = f

        data_points = [
            {"date": end, "value": float(f["val"])}
            for end, f in sorted(by_date.items())
        ]

        return data_points, f"{unit_key} ({label})", entity

    raise ValueError(
        f"Concept '{concept}' not found in EDGAR facts. "
        f"Known concepts: {', '.join(c[0] for c in EDGAR_CONCEPTS[:8])} ..."
    )


class EdgarService:
    """SEC EDGAR service for company fundamental time series."""

    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        series_id: TICKER:CONCEPT  (e.g. AAPL:Revenues)
        """
        try:
            if ":" not in series_id:
                raise ValueError(
                    f"Invalid series_id '{series_id}'. "
                    "Format: TICKER:CONCEPT  e.g. AAPL:Revenues"
                )
            ticker, concept = series_id.split(":", 1)
            ticker = ticker.upper().strip()
            concept = concept.strip()

            cik = _cik_for_ticker(ticker)
            time.sleep(0.1)  # respect SEC 10 req/s fair-use rate
            facts = _fetch_company_facts(cik)

            data_points, units, entity = _extract_series(facts, concept)

            # Date filtering
            if start_date:
                sd = start_date[:10]
                data_points = [d for d in data_points if d["date"] >= sd]
            if end_date:
                ed = end_date[:10]
                data_points = [d for d in data_points if d["date"] <= ed]

            title = (
                f"{entity} — {EDGAR_CONCEPTS_MAP.get(concept, concept)}"
            )
            return {
                "series_id": series_id,
                "title": title,
                "units": units,
                "frequency": "Annual / Quarterly",
                "seasonal_adjustment": "Not Seasonally Adjusted",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]["date"] if data_points else "",
                "observation_end": data_points[-1]["date"] if data_points else "",
                "data": data_points,
                "data_points": len(data_points),
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except requests.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"SEC EDGAR request failed: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching EDGAR series {series_id}: {e}",
            )

    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search available concepts (not companies — no company name search API)."""
        q = search_text.lower()
        matches = [
            (code, label)
            for code, label in EDGAR_CONCEPTS
            if q in code.lower() or q in label.lower()
        ][:limit]

        return {
            "query": search_text,
            "results": [
                {
                    "series_id": f"TICKER:{code}",
                    "title": f"{label} (replace TICKER with actual ticker)",
                    "units": "Various",
                    "frequency": "Annual / Quarterly",
                    "seasonal_adjustment": "Not Seasonally Adjusted",
                    "popularity": 0,
                }
                for code, label in matches
            ],
            "count": len(matches),
            "message": (
                "EDGAR series IDs use format TICKER:CONCEPT  e.g. AAPL:Revenues. "
                "Replace TICKER with the stock ticker (e.g. AAPL, MSFT, TSLA)."
            ),
        }

    def validate_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        if ":" not in symbol:
            return False, "Format must be TICKER:CONCEPT  e.g. AAPL:Revenues"
        ticker, concept = symbol.split(":", 1)
        if not ticker.strip():
            return False, "Ticker cannot be empty"
        if not concept.strip():
            return False, "Concept cannot be empty"
        return True, None

    def get_suggestions(
        self, query: str, category: Optional[str] = None, limit: int = 20
    ) -> List[Tuple[str, str]]:
        q = query.upper()
        return [
            (f"TICKER:{code}", "concept")
            for code, _ in EDGAR_CONCEPTS
            if q in code.upper()
        ][:limit]


_edgar_service: Optional[EdgarService] = None


def get_edgar_service() -> EdgarService:
    global _edgar_service
    if _edgar_service is None:
        _edgar_service = EdgarService()
    return _edgar_service
