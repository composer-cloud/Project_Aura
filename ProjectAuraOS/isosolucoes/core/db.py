"""
IsoSoluções - Canal Inteligente
Core database layer (SQLite) for leads, analyses, channels, signals.
Simple, auditable, no external deps beyond stdlib + sqlite3.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).parent.parent / "data" / "isosolucoes_canal.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    website TEXT,
    cnpj TEXT,
    industry TEXT,
    location TEXT,
    size_estimate TEXT,           -- ex: "80-150 funcionários", "médio porte"
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    probability INTEGER NOT NULL CHECK (probability BETWEEN 0 AND 100),
    probability_breakdown TEXT,   -- JSON: {"IATF_automotivo": +25, "ultimato_cliente": +18, ...}
    identity_summary TEXT,
    buyer_characteristics TEXT,   -- JSON or markdown rich text
    recommended_channels TEXT,    -- JSON array of channel ids + rationale
    suggested_next_action TEXT,
    raw_llm_output TEXT,
    model_used TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    signal_type TEXT NOT NULL,    -- 'positive' | 'negative' | 'conversion' | 'channel_result'
    description TEXT NOT NULL,
    channel_id TEXT,              -- if related to a channel
    impact_on_probability INTEGER, -- optional delta
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS channel_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    channel_id TEXT NOT NULL,
    quality_judgment INTEGER,     -- 1-5 or user override
    notes TEXT,
    outcome TEXT,                 -- 'no_contact', 'engaged', 'meeting', 'proposal', 'closed_won', 'closed_lost'
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_analyses_company ON analyses(company_id);
CREATE INDEX IF NOT EXISTS idx_signals_company ON signals(company_id);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

def now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

# --- Companies ---

def create_company(name: str, **kwargs) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO companies (name, website, cnpj, industry, location, size_estimate, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        kwargs.get("website"),
        kwargs.get("cnpj"),
        kwargs.get("industry"),
        kwargs.get("location"),
        kwargs.get("size_estimate"),
        kwargs.get("notes"),
        now()
    ))
    company_id = cur.lastrowid
    conn.commit()
    conn.close()
    return company_id

def list_companies() -> list[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM companies ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_company(company_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_company(company_id: int, **kwargs):
    conn = get_conn()
    fields = []
    values = []
    for k in ["name", "website", "cnpj", "industry", "location", "size_estimate", "notes"]:
        if k in kwargs:
            fields.append(f"{k} = ?")
            values.append(kwargs[k])
    if not fields:
        conn.close()
        return
    fields.append("updated_at = ?")
    values.append(now())
    values.append(company_id)
    conn.execute(f"UPDATE companies SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()

# --- Analyses ---

def save_analysis(company_id: int, data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analyses (
            company_id, probability, probability_breakdown, identity_summary,
            buyer_characteristics, recommended_channels, suggested_next_action,
            raw_llm_output, model_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_id,
        data.get("probability", 50),
        json.dumps(data.get("probability_breakdown", {}), ensure_ascii=False),
        data.get("identity_summary", ""),
        json.dumps(data.get("buyer_characteristics", {}), ensure_ascii=False) if isinstance(data.get("buyer_characteristics"), dict) else data.get("buyer_characteristics", ""),
        json.dumps(data.get("recommended_channels", []), ensure_ascii=False),
        data.get("suggested_next_action", ""),
        data.get("raw_llm_output", ""),
        data.get("model_used", "ollama-local")
    ))
    analysis_id = cur.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_latest_analysis(company_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("""
        SELECT * FROM analyses 
        WHERE company_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (company_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    for k in ["probability_breakdown", "buyer_characteristics", "recommended_channels"]:
        if d.get(k):
            try:
                d[k] = json.loads(d[k])
            except Exception:
                pass
    return d

# --- Signals ---

def add_signal(company_id: int, signal_type: str, description: str, channel_id: Optional[str] = None, impact: Optional[int] = None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO signals (company_id, signal_type, description, channel_id, impact_on_probability)
        VALUES (?, ?, ?, ?, ?)
    """, (company_id, signal_type, description, channel_id, impact))
    conn.commit()
    conn.close()

def list_signals(company_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM signals WHERE company_id = ? ORDER BY created_at DESC
    """, (company_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Channel evaluations ---

def record_channel_outcome(company_id: int, channel_id: str, outcome: str, notes: str = "", quality: Optional[int] = None):
    conn = get_conn()
    conn.execute("""
        INSERT INTO channel_evaluations (company_id, channel_id, outcome, notes, quality_judgment)
        VALUES (?, ?, ?, ?, ?)
    """, (company_id, channel_id, outcome, notes, quality))
    conn.commit()
    conn.close()

def get_company_channel_history(company_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM channel_evaluations WHERE company_id = ? ORDER BY created_at DESC
    """, (company_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db()
    print("DB initialized at", DB_PATH)
