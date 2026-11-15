"""SQLite Database Persistence for Jobs, Checkpoints, and Scanned Opportunities."""

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("gigbid.db")
DB_PATH = Path(__file__).resolve().parents[2] / "gigbid.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                subcategory TEXT,
                skills TEXT,
                job_type TEXT,
                budget_usd REAL,
                hourly_rate_min REAL,
                hourly_rate_max REAL,
                estimated_duration TEXT,
                client_id TEXT,
                posted_at TEXT,
                connects_required INTEGER,
                source TEXT,
                raw_json TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_jobs(jobs: List[Dict[str, Any]]):
    init_db()
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc).isoformat()
        for j in jobs:
            skills_val = j.get("skills", [])
            skills_str = json.dumps(skills_val) if isinstance(skills_val, list) else str(skills_val)
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs (
                    id, title, description, category, subcategory, skills,
                    job_type, budget_usd, hourly_rate_min, hourly_rate_max,
                    estimated_duration, client_id, posted_at, connects_required,
                    source, raw_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(j.get("id")),
                    str(j.get("title", "")),
                    str(j.get("description", "")),
                    str(j.get("category", "")),
                    str(j.get("subcategory", "")),
                    skills_str,
                    str(j.get("job_type", "fixed_price")),
                    float(j["budget_usd"]) if j.get("budget_usd") is not None else None,
                    float(j["hourly_rate_min"]) if j.get("hourly_rate_min") is not None else None,
                    float(j["hourly_rate_max"]) if j.get("hourly_rate_max") is not None else None,
                    str(j.get("estimated_duration", "")),
                    str(j.get("client_id", "")),
                    str(j.get("posted_at", now)),
                    int(j.get("connects_required", 16)),
                    str(j.get("source", "upwork_live")),
                    json.dumps(j),
                    now,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def get_all_jobs(source: Optional[str] = None) -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    try:
        if source:
            rows = conn.execute("SELECT raw_json FROM jobs WHERE source = ?", (source,)).fetchall()
        else:
            rows = conn.execute("SELECT raw_json FROM jobs").fetchall()
        results = []
        for r in rows:
            try:
                results.append(json.loads(r["raw_json"]))
            except Exception:
                pass
        return results
    finally:
        conn.close()


def clear_dummy_seed_jobs():
    init_db()
    conn = get_connection()
    try:
        conn.execute("DELETE FROM jobs WHERE source != 'upwork_live' OR id LIKE 'job_0%'")
        conn.commit()
    finally:
        conn.close()
