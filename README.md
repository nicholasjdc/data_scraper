# Provenance

A personal economic datum dashboard that treats data provenance as a first-class feature. Every data point is traceable to the exact API call that produced it. An AI analysis layer (Claude) is architecturally constrained to only reason from data that was explicitly fetched from a source API — it cannot draw on training-time knowledge for specific economic values.

---

## Data Sources

| Source | What it provides | API Key |
|--------|-----------------|---------|
| [FRED](https://fred.stlouisfed.org/) | U.S. economic series (GDP, unemployment, CPI, ...) | Required |
| [World Bank](https://data.worldbank.org/) | Global economic indicators | — |
| [U.S. Census Bureau](https://www.census.gov/data/developers.html) | U.S. demographic & economic data | — |
| [Alpha Vantage](https://www.alphavantage.co/) | Stocks, forex, crypto | Required |
| [Yahoo Finance](https://finance.yahoo.com/) | Market data, ETFs, indices | — |

---

## Provenance Model

Every API call writes an immutable record to a local SQLite database before any data reaches the UI:

| Field | Description |
|-------|-------------|
| `fetch_id` | UUID that travels with the data through the UI |
| `source` | "fred", "worldbank", "alphavantage", etc. |
| `series_id` | The exact identifier used to fetch |
| `request_params` | Every parameter passed to the API |
| `fetched_at` | UTC timestamp of the fetch |
| `response_sha256` | SHA-256 fingerprint of the response — changes if upstream data is revised |
| `response_body` | Full normalized response, stored as-fetched |
| `latency_ms` | Fetch duration |

Each graph card shows a provenance badge: **`FRED:UNRATE • fetched 14:23 UTC`**. Clicking it opens the raw fetch record so you can see exactly what the API returned, when, and with what parameters.

Inspired by [FRED/ALFRED's vintage model](https://alfred.stlouisfed.org/), [Datasette's hierarchical metadata](https://datasette.io/), and [AlphaSense's cited-snippet approach](https://www.alpha-sense.com/).

---

## AI Layer

Claude operates as an additional analysis layer, not a data source. It is constrained in two ways:

**1. Must call to fetch.** The AI has access to a `fetch_series` tool that triggers a real API call and records provenance. It cannot answer from training weights for specific values — it must call the tool to get data.

**2. Must cite every claim.** The AI is required to submit its analysis via a `submit_analysis` tool call. Every quantitative claim is a structured object:

```json
{
  "text": "Unemployment rose to 4.2% in March 2024",
  "fetch_id": "3f8a1c2d-...",
  "series_id": "UNRATE",
  "date": "2024-03-01",
  "value": 4.2
}
```

After the AI responds, each claim is verified: the cited `(date, value)` pair must actually appear in the fetch record it referenced. The verification result is stored and shown in the UI.

Every AI analysis is stored in a dedicated table:

| Field | Description |
|-------|-------------|
| `analysis_id` | UUID |
| `model_id` | e.g. "claude-sonnet-4-6" |
| `input_fetch_ids` | Every fetch record the AI had access to |
| `claims` | Each claim with its verification status |
| `verified` | Whether all citations checked out |

---

## Setup

```bash
# Backend
pip install -r app/requirements.txt
cp .env.example .env        # fill in API keys
python run.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Environment variables

```
FRED_API_KEY=...            # fred.stlouisfed.org — free
ALPHA_VANTAGE_API_KEY=...   # alphavantage.co — free
ANTHROPIC_API_KEY=...       # console.anthropic.com — required for AI analysis
```

---

## Architecture

```
User → React UI
  → FastAPI backend
    → Service layer (FRED / World Bank / Census / Alpha Vantage / yfinance)
    → record_fetch() → provenance.db  (raw_fetches table)
    → SeriesResponse { fetch_id, fetched_at, data, ... }
  → UI: graph card with provenance badge

User clicks "Analyze with AI":
  → POST /api/v1/ai/analyze { fetch_ids, question }
  → Claude receives SOURCE_BLOCKs built from fetch records
  → Claude calls fetch_series tool if it needs additional data
    → real API call → provenance recorded → data returned with fetch_id
  → Claude calls submit_analysis with structured claims
  → Claims verified against raw fetch records
  → Analysis stored in ai_analyses table
  → UI: summary + per-claim provenance badges (verified/unverified)
```

---

## Stack

**Backend** — FastAPI, SQLite (provenance store), Anthropic SDK
**Frontend** — React 18, TypeScript, Recharts
