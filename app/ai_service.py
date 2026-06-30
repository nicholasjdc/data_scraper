"""
AI analysis layer using Claude with mandatory tool-use.

The AI must call `fetch_series` to retrieve any data it references,
and must call `submit_analysis` to produce structured output with citations.
It cannot generate free-text economic values from training knowledge.
"""

import json
import time
from typing import Any, Dict, List, Optional

import anthropic

from app.config import settings
from app.provenance import get_fetch_record, record_fetch, record_ai_analysis, verify_claims
from app.service_router import get_service

MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "fetch_series",
        "description": (
            "Fetch economic data from a source API. "
            "You MUST call this tool before referencing any specific numeric value in your analysis. "
            "All fetches are recorded for provenance. "
            "Available sources: fred, alphavantage, yfinance, worldbank."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "series_id": {
                    "type": "string",
                    "description": "Series identifier (e.g. UNRATE, GDP for fred; AAPL for yfinance; NY.GDP.MKTP.CD for worldbank)",
                },
                "source": {
                    "type": "string",
                    "enum": ["fred", "alphavantage", "yfinance", "worldbank"],
                },
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["series_id", "source"],
        },
    },
    {
        "name": "submit_analysis",
        "description": (
            "Submit your final analysis. Call this when you are ready to present your findings. "
            "Every quantitative claim MUST include fetch_id, series_id, date, and value "
            "from a SOURCE_BLOCK or a fetch_series tool result."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "2-4 sentence overview of the trends and findings.",
                },
                "claims": {
                    "type": "array",
                    "description": "Each specific quantitative claim, with its provenance citation.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "fetch_id": {"type": "string"},
                            "series_id": {"type": "string"},
                            "date": {"type": "string", "description": "YYYY-MM-DD"},
                            "value": {"type": "number"},
                        },
                        "required": ["text", "fetch_id", "series_id", "date", "value"],
                    },
                },
                "data_gaps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "What additional data would improve this analysis.",
                },
            },
            "required": ["summary", "claims"],
        },
    },
]

SYSTEM_PROMPT = """You are an economic data analyst. You have access to explicitly fetched data series.

CRITICAL RULES:
1. For any specific numeric value you cite (a rate, index level, dollar figure, etc.), you MUST reference a SOURCE_BLOCK fetch_id or call fetch_series first.
2. Do NOT recall specific economic values from training knowledge — only cite what appears in the SOURCE_BLOCKs or what you retrieved via fetch_series.
3. General economic interpretation, trend direction, and contextual commentary do not require citations.
4. If you want data that is not in the SOURCE_BLOCKs, call fetch_series before submitting your analysis.
5. You MUST end by calling submit_analysis with structured claims."""


def _build_source_block(record: Dict) -> str:
    body = record["response_body"]
    data_points = body.get("data", [])
    recent = data_points[-24:] if len(data_points) > 24 else data_points
    obs_lines = "\n".join(
        f"  {pt['date']}: {pt['value']}"
        for pt in recent
        if pt.get("value") is not None
    )
    return (
        f"[SOURCE_BLOCK]\n"
        f"fetch_id: {record['fetch_id']}\n"
        f"source: {record['source']}\n"
        f"series_id: {record['series_id']}\n"
        f"title: {body.get('title', '')}\n"
        f"units: {body.get('units', '')}\n"
        f"frequency: {body.get('frequency', '')}\n"
        f"fetched_at: {record['fetched_at']}\n"
        f"observations (most recent {len(recent)}):\n"
        f"{obs_lines}\n"
        f"[/SOURCE_BLOCK]"
    )


def _execute_fetch_tool(
    series_id: str,
    source: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Call the real service, record provenance, return data with fetch_id."""
    service = get_service(source)
    params: Dict[str, Any] = {"series_id": series_id, "source": source}
    call_kwargs: Dict[str, Any] = {"series_id": series_id}
    if start_date:
        params["start_date"] = start_date
        call_kwargs["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
        call_kwargs["end_date"] = end_date

    t0 = time.monotonic()
    result = service.get_series(**call_kwargs)
    latency_ms = int((time.monotonic() - t0) * 1000)

    fetch_id, fetched_at = record_fetch(
        source=source,
        series_id=series_id,
        request_params=params,
        response_body=result,
        latency_ms=latency_ms,
    )
    result["fetch_id"] = fetch_id
    result["fetched_at"] = fetched_at
    result["source"] = source
    return result


def analyze(fetch_ids: List[str], question: Optional[str]) -> Dict[str, Any]:
    """
    Run a Claude analysis over the given fetch records.

    Claude receives SOURCE_BLOCKs for each fetch_id, may call fetch_series
    for additional data, and must call submit_analysis with structured claims.
    Returns a dict suitable for the API response.
    """
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Load existing fetch records
    fetch_records: Dict[str, Dict] = {}
    source_blocks: List[str] = []
    for fid in fetch_ids:
        record = get_fetch_record(fid)
        if record:
            fetch_records[fid] = record
            source_blocks.append(_build_source_block(record))

    if not source_blocks:
        raise ValueError("No valid fetch records found for the provided fetch_ids")

    user_content = "\n\n".join(source_blocks)
    user_content += f"\n\nQuestion: {question or 'Analyze the trends in these economic data series.'}"

    messages: List[Dict] = [{"role": "user", "content": user_content}]
    all_fetch_ids = list(fetch_ids)
    analysis_input: Optional[Dict] = None

    for _ in range(10):  # guard against infinite tool loops
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "any"},
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            if block.name == "submit_analysis":
                analysis_input = block.input
                # Acknowledge the tool call so the conversation is valid
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "Analysis submitted.",
                })

            elif block.name == "fetch_series":
                inp = block.input
                try:
                    fetched = _execute_fetch_tool(
                        series_id=inp["series_id"],
                        source=inp["source"],
                        start_date=inp.get("start_date"),
                        end_date=inp.get("end_date"),
                    )
                    new_fid = fetched["fetch_id"]
                    all_fetch_ids.append(new_fid)
                    new_record = get_fetch_record(new_fid)
                    if new_record:
                        fetch_records[new_fid] = new_record
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(fetched, default=str),
                    })
                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error fetching {inp.get('series_id')}: {e}",
                        "is_error": True,
                    })

        if analysis_input is not None:
            break

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    if analysis_input is None:
        raise ValueError("AI did not produce an analysis within the allowed iterations")

    claims = verify_claims(analysis_input.get("claims", []), fetch_records)
    verified = bool(claims) and all(c.get("verified", False) for c in claims)

    analysis_id = record_ai_analysis(
        model_id=MODEL,
        prompt=user_content,
        input_fetch_ids=all_fetch_ids,
        response_body={**analysis_input, "claims": claims},
        verified=verified,
    )

    return {
        "analysis_id": analysis_id,
        "model_id": MODEL,
        "summary": analysis_input.get("summary", ""),
        "claims": claims,
        "data_gaps": analysis_input.get("data_gaps", []),
        "input_fetch_ids": all_fetch_ids,
        "verified": verified,
    }
