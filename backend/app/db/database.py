import sqlite3

DB_PATH = "tracepilot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traces (
        trace_id TEXT PRIMARY KEY,
        query TEXT,
        retrieved_chunks TEXT,
        prompt TEXT,
        response TEXT,
        latency REAL,
        timestamp TEXT,
        model_name TEXT,
        retrieval_score_avg REAL,
        response_length INTEGER,
        chunk_count INTEGER,
        parent_trace_id TEXT,
        retrieval_quality TEXT,
        grounded BOOLEAN,
        top_retrieval_score REAL,
        spans TEXT,
        failure_types TEXT,
        prompt_mode TEXT DEFAULT 'strict'
    )
    """)

    conn.commit()
    conn.close()
