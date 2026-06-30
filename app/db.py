import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "provenance.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS raw_fetches (
                fetch_id        TEXT PRIMARY KEY,
                source          TEXT NOT NULL,
                series_id       TEXT NOT NULL,
                request_params  TEXT NOT NULL,
                fetched_at      TEXT NOT NULL,
                response_sha256 TEXT NOT NULL,
                response_body   TEXT NOT NULL,
                latency_ms      INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_rf_source_series
                ON raw_fetches(source, series_id);
            CREATE INDEX IF NOT EXISTS idx_rf_fetched_at
                ON raw_fetches(fetched_at DESC);

            CREATE TABLE IF NOT EXISTS ai_analyses (
                analysis_id     TEXT PRIMARY KEY,
                created_at      TEXT NOT NULL,
                model_id        TEXT NOT NULL,
                prompt_sha256   TEXT NOT NULL,
                input_fetch_ids TEXT NOT NULL,
                response_body   TEXT NOT NULL,
                verified        INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_ai_created_at
                ON ai_analyses(created_at DESC);
        """)
        conn.commit()
    finally:
        conn.close()
