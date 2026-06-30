import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.db import get_db


def _sha256_json(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def record_fetch(
    source: str,
    series_id: str,
    request_params: Dict[str, Any],
    response_body: Any,
    latency_ms: int,
) -> Tuple[str, str]:
    """Write a raw fetch record and return (fetch_id, fetched_at)."""
    fetch_id = str(uuid.uuid4())
    fetched_at = datetime.now(timezone.utc).isoformat()

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO raw_fetches
               (fetch_id, source, series_id, request_params, fetched_at,
                response_sha256, response_body, latency_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fetch_id,
                source,
                series_id,
                json.dumps(request_params, default=str),
                fetched_at,
                _sha256_json(response_body),
                json.dumps(response_body, default=str),
                latency_ms,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return fetch_id, fetched_at


def get_fetch_record(fetch_id: str) -> Optional[Dict]:
    """Return a fetch record by ID, or None if not found."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM raw_fetches WHERE fetch_id = ?", (fetch_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["request_params"] = json.loads(d["request_params"])
        d["response_body"] = json.loads(d["response_body"])
        return d
    finally:
        conn.close()


def record_ai_analysis(
    model_id: str,
    prompt: str,
    input_fetch_ids: List[str],
    response_body: Any,
    verified: bool,
) -> str:
    """Store an AI analysis run and return its analysis_id."""
    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO ai_analyses
               (analysis_id, created_at, model_id, prompt_sha256,
                input_fetch_ids, response_body, verified)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                analysis_id,
                created_at,
                model_id,
                hashlib.sha256(prompt.encode()).hexdigest(),
                json.dumps(input_fetch_ids),
                json.dumps(response_body, default=str),
                1 if verified else 0,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return analysis_id


def verify_claims(claims: List[Dict], fetch_records: Dict[str, Dict]) -> List[Dict]:
    """
    Check each claim's cited (date, value) against its fetch record.
    Returns claims with an added 'verified' bool and 'verification_note'.
    """
    out = []
    for claim in claims:
        fid = claim.get("fetch_id", "")
        record = fetch_records.get(fid)

        if record is None:
            out.append({**claim, "verified": False, "verification_note": "fetch_id not in context"})
            continue

        cited_date = str(claim.get("date", ""))
        cited_value = claim.get("value")

        if cited_date and cited_value is not None:
            data_points = record["response_body"].get("data", [])
            match = any(
                str(pt.get("date", "")).startswith(cited_date[:10])
                and pt.get("value") is not None
                and abs(float(pt["value"]) - float(cited_value)) < 0.01
                for pt in data_points
            )
            note = "ok" if match else f"{cited_value} not found for {cited_date}"
        else:
            match = False
            note = "missing date or value in claim"

        out.append({**claim, "verified": match, "verification_note": note})

    return out
