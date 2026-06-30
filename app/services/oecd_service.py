"""
OECD service — international quarterly macro data via SDMX-JSON.

Series ID format:  DATASET:KEY
  e.g.  QNA:USA.B1_GS1.GYSA.Q        — U.S. quarterly GDP growth (YoY SA)
        QNA:DEU.B1_GS1.GYSA.Q        — Germany quarterly GDP growth
        QNA:GBR.B1_GS1.GYSA.Q        — U.K. quarterly GDP growth
        MEI:USA.LRHUTTTT.ST.M         — U.S. unemployment rate (monthly)
        MEI:DEU.LRHUTTTT.ST.M         — Germany unemployment rate
        PRICES_CPI:USA.CPALTT01.GY.M  — U.S. CPI (all items, YoY)
        EO:USA.IRLONG.Q               — U.S. long-term interest rate
        EO:USA.IRSTR.Q                — U.S. short-term interest rate

Datasets:
  QNA   — Quarterly National Accounts (GDP, consumption, investment, trade)
  MEI   — Main Economic Indicators (unemployment, IP, CPI, trade balance)
  PRICES_CPI — Consumer Prices
  EO    — Economic Outlook (OECD forecasts + actuals)
  BILOR — Balance of Payments
  NATDIFF — National Accounts Disaggregated

Country codes (ISO 3166-1 alpha-3):
  USA, DEU, GBR, FRA, JPN, CAN, ITA, AUS, KOR, NLD, ...

No API key required. No documented rate limit.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import HTTPException


_BASE = "https://stats.oecd.org/SDMX-JSON/data"

# Curated list of useful series for autocomplete / search
OECD_SERIES = [
    # GDP
    ("QNA:USA.B1_GS1.GYSA.Q",        "USA — GDP growth rate (QoQ SA, quarterly)"),
    ("QNA:DEU.B1_GS1.GYSA.Q",        "Germany — GDP growth rate (QoQ SA, quarterly)"),
    ("QNA:GBR.B1_GS1.GYSA.Q",        "UK — GDP growth rate (QoQ SA, quarterly)"),
    ("QNA:JPN.B1_GS1.GYSA.Q",        "Japan — GDP growth rate (QoQ SA, quarterly)"),
    ("QNA:FRA.B1_GS1.GYSA.Q",        "France — GDP growth rate (QoQ SA, quarterly)"),
    ("QNA:CAN.B1_GS1.GYSA.Q",        "Canada — GDP growth rate (QoQ SA, quarterly)"),
    ("QNA:KOR.B1_GS1.GYSA.Q",        "Korea — GDP growth rate (QoQ SA, quarterly)"),
    # Unemployment
    ("MEI:USA.LRHUTTTT.ST.M",         "USA — Unemployment rate (monthly, SA)"),
    ("MEI:DEU.LRHUTTTT.ST.M",         "Germany — Unemployment rate (monthly, SA)"),
    ("MEI:GBR.LRHUTTTT.ST.M",         "UK — Unemployment rate (monthly, SA)"),
    ("MEI:JPN.LRHUTTTT.ST.M",         "Japan — Unemployment rate (monthly, SA)"),
    ("MEI:FRA.LRHUTTTT.ST.M",         "France — Unemployment rate (monthly, SA)"),
    # CPI
    ("PRICES_CPI:USA.CPALTT01.GY.M",  "USA — CPI all items YoY (monthly)"),
    ("PRICES_CPI:DEU.CPALTT01.GY.M",  "Germany — CPI all items YoY (monthly)"),
    ("PRICES_CPI:GBR.CPALTT01.GY.M",  "UK — CPI all items YoY (monthly)"),
    ("PRICES_CPI:JPN.CPALTT01.GY.M",  "Japan — CPI all items YoY (monthly)"),
    # Interest rates
    ("EO:USA.IRLONG.Q",               "USA — Long-term interest rate (quarterly)"),
    ("EO:DEU.IRLONG.Q",               "Germany — Long-term interest rate (quarterly)"),
    ("EO:USA.IRSTR.Q",                "USA — Short-term interest rate (quarterly)"),
    # Industrial production
    ("MEI:USA.PRINTO01.IX.M",         "USA — Industrial production index (monthly)"),
    ("MEI:DEU.PRINTO01.IX.M",         "Germany — Industrial production index (monthly)"),
    # Trade
    ("MEI:USA.BPBLTT01.STSA.M",       "USA — Trade balance (monthly, SA)"),
]

OECD_SERIES_MAP = {s[0]: s[1] for s in OECD_SERIES}


def _parse_sdmx_json(payload: Dict, series_id: str) -> List[Dict]:
    """
    Parse OECD SDMX-JSON response into a list of {date, value} dicts.
    Handles both 'series' (grouped) and flat observation structures.
    """
    try:
        data_sets = payload.get("dataSets", [])
        structure = payload.get("structure", {})
        dims = structure.get("dimensions", {})

        obs_dims = dims.get("observation", [])
        ser_dims = dims.get("series", [])

        # Find TIME_PERIOD dimension in observation dimensions
        time_dim = next(
            (d for d in obs_dims if d.get("id") == "TIME_PERIOD"), None
        )
        if time_dim is None:
            # Some responses put time in series dimensions
            time_dim = next(
                (d for d in ser_dims if d.get("id") == "TIME_PERIOD"), None
            )

        time_values = [v["id"] for v in (time_dim or {}).get("values", [])]

        data_points = []

        for ds in data_sets:
            # Flat observation layout (dimensionAtObservation=allDimensions)
            if "observations" in ds:
                for key, obs in ds["observations"].items():
                    indices = list(map(int, key.split(":")))
                    if obs and obs[0] is not None:
                        # Time index is last dimension for allDimensions layout
                        t_idx = indices[-1]
                        date = time_values[t_idx] if t_idx < len(time_values) else key
                        data_points.append({"date": date, "value": float(obs[0])})

            # Series layout
            elif "series" in ds:
                for _ser_key, ser_data in ds["series"].items():
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
        raise ValueError(f"Failed to parse OECD SDMX response for {series_id}: {e}")


def _oecd_date_to_iso(period: str) -> str:
    """Convert OECD period strings (2020-Q1, 2020-01, 2020) to ISO dates."""
    if re.match(r"^\d{4}-Q\d$", period):
        year, q = period.split("-Q")
        month = str((int(q) - 1) * 3 + 1).zfill(2)
        return f"{year}-{month}-01"
    if re.match(r"^\d{4}-\d{2}$", period):
        return f"{period}-01"
    if re.match(r"^\d{4}$", period):
        return f"{period}-01-01"
    return period


import re


class OECDService:
    """OECD SDMX-JSON service for international macro data."""

    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        series_id: DATASET:KEY  (e.g. QNA:USA.B1_GS1.GYSA.Q)
        """
        try:
            if ":" not in series_id:
                raise ValueError(
                    f"Invalid series_id '{series_id}'. "
                    "Format: DATASET:KEY  e.g. QNA:USA.B1_GS1.GYSA.Q"
                )
            dataset, key = series_id.split(":", 1)
            dataset = dataset.upper().strip()
            key = key.strip()

            params: Dict[str, str] = {"dimensionAtObservation": "allDimensions"}
            if start_date:
                params["startTime"] = start_date[:4]
            if end_date:
                params["endTime"] = end_date[:4]

            url = f"{_BASE}/{dataset}/{key}/all"
            resp = requests.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
                timeout=60,
            )
            resp.raise_for_status()
            payload = resp.json()

            data_points = _parse_sdmx_json(payload, series_id)

            # Convert OECD period strings to ISO dates
            data_points = [
                {"date": _oecd_date_to_iso(d["date"]), "value": d["value"]}
                for d in data_points
            ]

            # Apply date filtering
            if start_date:
                sd = start_date[:10]
                data_points = [d for d in data_points if d["date"] >= sd]
            if end_date:
                ed = end_date[:10]
                data_points = [d for d in data_points if d["date"] <= ed]

            title = OECD_SERIES_MAP.get(series_id, f"OECD {dataset}: {key}")

            # Infer frequency from key suffix
            freq = "Unknown"
            if key.endswith(".Q"):
                freq = "Quarterly"
            elif key.endswith(".M") or key.endswith(".A"):
                freq = "Monthly" if key.endswith(".M") else "Annual"

            return {
                "series_id": series_id,
                "title": title,
                "units": "",
                "frequency": freq,
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
            raise HTTPException(
                status_code=502,
                detail=f"OECD API request failed: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching OECD series {series_id}: {e}",
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
            for sid, label in OECD_SERIES
            if q in sid.lower() or q in label.lower()
        ][:limit]

        return {
            "query": search_text,
            "results": [
                {
                    "series_id": sid,
                    "title": label,
                    "units": "",
                    "frequency": "Quarterly/Monthly",
                    "seasonal_adjustment": "See series key",
                    "popularity": 0,
                }
                for sid, label in matches
            ],
            "count": len(matches),
        }

    def validate_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        if ":" not in symbol:
            return False, "Format must be DATASET:KEY  e.g. QNA:USA.B1_GS1.GYSA.Q"
        dataset, key = symbol.split(":", 1)
        if not dataset.strip():
            return False, "Dataset cannot be empty"
        if not key.strip():
            return False, "Key cannot be empty"
        return True, None

    def get_suggestions(
        self, query: str, category: Optional[str] = None, limit: int = 20
    ) -> List[Tuple[str, str]]:
        q = query.upper()
        return [
            (sid, "oecd")
            for sid, _ in OECD_SERIES
            if q in sid.upper()
        ][:limit]


_oecd_service: Optional[OECDService] = None


def get_oecd_service() -> OECDService:
    global _oecd_service
    if _oecd_service is None:
        _oecd_service = OECDService()
    return _oecd_service
