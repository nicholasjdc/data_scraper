"""
ECB (European Central Bank) service — eurozone monetary policy and macro data.

Series ID format:  FLOW/KEY
  e.g.  FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN   — Main refinancing rate
        FM/B.U2.EUR.RT0.BB.1000.00.DFR.AN        — Deposit facility rate
        FM/B.U2.EUR.RT0.BB.1000.00.MLF_RT.AN     — Marginal lending facility rate
        ICP/M.U2.N.000000.4.ANR                  — HICP all-items YoY (eurozone)
        ICP/M.U2.N.010000.4.ANR                  — HICP food YoY
        ICP/M.U2.N.072000.4.ANR                  — HICP transport YoY
        BSI/M.U2.N.A.L20.A.1.U2.2300.Z01.E       — Loans to non-financial corps
        EXR/D.USD.EUR.SP00.A                      — USD/EUR reference rate (daily)
        EXR/M.GBP.EUR.SP00.A                      — GBP/EUR reference rate (monthly)
        EXR/M.JPY.EUR.SP00.A                      — JPY/EUR reference rate (monthly)
        GST/A.DE.MGDP.Y                           — Germany GDP
        ILM/M.U2.S121.A.F.A50.A.1.Z5.0000.Z01.E  — M3 money supply

Dataflows:
  FM    — Financial market data (ECB key rates)
  ICP   — Consumer prices (HICP)
  BSI   — Balance sheet items (bank lending)
  EXR   — Exchange rates
  ILM   — Liquidity conditions (money supply, M1/M2/M3)
  GST   — Government finance statistics

API: https://data-api.ecb.europa.eu/service/data/{FLOW}/{KEY}?format=jsondata
No API key required. No documented rate limits.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import HTTPException


_BASE = "https://data-api.ecb.europa.eu/service/data"

ECB_SERIES = [
    # ECB key rates
    ("FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN", "ECB main refinancing rate"),
    ("FM/B.U2.EUR.RT0.BB.1000.00.DFR.AN",    "ECB deposit facility rate"),
    ("FM/B.U2.EUR.RT0.BB.1000.00.MLF_RT.AN", "ECB marginal lending facility rate"),
    # HICP inflation
    ("ICP/M.U2.N.000000.4.ANR",  "Eurozone HICP all-items YoY (monthly)"),
    ("ICP/M.U2.N.010000.4.ANR",  "Eurozone HICP food YoY (monthly)"),
    ("ICP/M.U2.N.040000.4.ANR",  "Eurozone HICP housing & energy YoY (monthly)"),
    ("ICP/M.U2.N.072000.4.ANR",  "Eurozone HICP transport YoY (monthly)"),
    ("ICP/M.U2.N.000000.4.ANR",  "Eurozone HICP all-items YoY"),
    # Exchange rates (ECB reference, published daily at 4pm Frankfurt)
    ("EXR/D.USD.EUR.SP00.A",  "USD/EUR exchange rate (daily reference)"),
    ("EXR/D.GBP.EUR.SP00.A",  "GBP/EUR exchange rate (daily reference)"),
    ("EXR/D.JPY.EUR.SP00.A",  "JPY/EUR exchange rate (daily reference)"),
    ("EXR/D.CHF.EUR.SP00.A",  "CHF/EUR exchange rate (daily reference)"),
    ("EXR/D.CNY.EUR.SP00.A",  "CNY/EUR exchange rate (daily reference)"),
    ("EXR/M.USD.EUR.SP00.A",  "USD/EUR exchange rate (monthly average)"),
    # Money supply
    ("ILM/M.U2.S1.A.F.A20.A.1.Z5.0000.Z01.E", "Eurozone M1 money supply (monthly)"),
    ("ILM/M.U2.S1.A.F.A30.A.1.Z5.0000.Z01.E", "Eurozone M2 money supply (monthly)"),
    ("ILM/M.U2.S1.A.F.A40.A.1.Z5.0000.Z01.E", "Eurozone M3 money supply (monthly)"),
    # Bank lending
    ("BSI/M.U2.N.A.L20.A.1.U2.2300.Z01.E", "Loans to non-financial corporations (monthly)"),
    ("BSI/M.U2.N.A.L20.A.1.U2.2250.Z01.E", "Loans to households (monthly)"),
]

ECB_SERIES_MAP = {s[0]: s[1] for s in ECB_SERIES}


def _parse_ecb_jsondata(payload: Dict, series_id: str) -> List[Dict]:
    """Parse ECB SDMX-JSON (format=jsondata) response into {date, value} list."""
    try:
        data_sets = payload.get("dataSets", [])
        structure = payload.get("structure", {})
        dims = structure.get("dimensions", {})

        obs_dims = dims.get("observation", [])
        time_dim = next(
            (d for d in obs_dims if d.get("id") == "TIME_PERIOD"), None
        )
        time_values = [v["id"] for v in (time_dim or {}).get("values", [])]

        data_points = []
        for ds in data_sets:
            for _ser_key, ser_data in ds.get("series", {}).items():
                for obs_key, obs in ser_data.get("observations", {}).items():
                    t_idx = int(obs_key)
                    if obs and obs[0] is not None and t_idx < len(time_values):
                        data_points.append({
                            "date": time_values[t_idx],
                            "value": float(obs[0]),
                        })

        data_points.sort(key=lambda x: x["date"])
        return data_points

    except Exception as e:
        raise ValueError(f"Failed to parse ECB SDMX response for {series_id}: {e}")


def _ecb_date_to_iso(period: str) -> str:
    """Convert ECB period strings (2020-Q1, 2020-01, 2020) to ISO dates."""
    import re
    if re.match(r"^\d{4}-Q\d$", period):
        year, q = period.split("-Q")
        month = str((int(q) - 1) * 3 + 1).zfill(2)
        return f"{year}-{month}-01"
    if re.match(r"^\d{4}-\d{2}$", period):
        return f"{period}-01"
    if re.match(r"^\d{4}$", period):
        return f"{period}-01-01"
    return period


class ECBService:
    """European Central Bank data service."""

    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        series_id: FLOW/KEY  (e.g. FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN)
        """
        try:
            if "/" not in series_id:
                raise ValueError(
                    f"Invalid series_id '{series_id}'. "
                    "Format: FLOW/KEY  e.g. FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN"
                )

            flow, key = series_id.split("/", 1)
            url = f"{_BASE}/{flow}/{key}"
            params: Dict[str, str] = {"format": "jsondata"}
            if start_date:
                params["startPeriod"] = start_date[:7]
            if end_date:
                params["endPeriod"] = end_date[:7]

            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            payload = resp.json()

            data_points = _parse_ecb_jsondata(payload, series_id)
            data_points = [
                {"date": _ecb_date_to_iso(d["date"]), "value": d["value"]}
                for d in data_points
            ]

            if start_date:
                data_points = [d for d in data_points if d["date"] >= start_date[:10]]
            if end_date:
                data_points = [d for d in data_points if d["date"] <= end_date[:10]]

            title = ECB_SERIES_MAP.get(series_id, f"ECB {flow}: {key}")

            return {
                "series_id": series_id,
                "title": title,
                "units": "",
                "frequency": "See series key",
                "seasonal_adjustment": "See series key",
                "last_updated": datetime.now().isoformat(),
                "observation_start": data_points[0]["date"] if data_points else "",
                "observation_end": data_points[-1]["date"] if data_points else "",
                "data": data_points,
                "data_points": len(data_points),
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except requests.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"ECB API request failed: {e}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching ECB series {series_id}: {e}",
            )

    def search_series(
        self,
        search_text: str,
        limit: int = 20,
        order_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        q = search_text.lower()
        matches = [
            (sid, label)
            for sid, label in ECB_SERIES
            if q in sid.lower() or q in label.lower()
        ][:limit]
        return {
            "query": search_text,
            "results": [
                {
                    "series_id": sid,
                    "title": label,
                    "units": "",
                    "frequency": "Daily/Monthly",
                    "seasonal_adjustment": "See series key",
                    "popularity": 0,
                }
                for sid, label in matches
            ],
            "count": len(matches),
        }

    def validate_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        if "/" not in symbol:
            return False, "Format must be FLOW/KEY  e.g. FM/B.U2.EUR.RT0.BB.1000.00.MRR_FR.AN"
        flow, key = symbol.split("/", 1)
        if not flow.strip():
            return False, "Flow cannot be empty"
        if not key.strip():
            return False, "Key cannot be empty"
        return True, None

    def get_suggestions(
        self, query: str, category: Optional[str] = None, limit: int = 20
    ) -> List[Tuple[str, str]]:
        q = query.upper()
        return [
            (sid, "ecb")
            for sid, _ in ECB_SERIES
            if q in sid.upper()
        ][:limit]


_ecb_service: Optional[ECBService] = None


def get_ecb_service() -> ECBService:
    global _ecb_service
    if _ecb_service is None:
        _ecb_service = ECBService()
    return _ecb_service
