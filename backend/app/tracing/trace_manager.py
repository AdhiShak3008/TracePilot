import json

from app.db.database import get_connection
from app.models.trace import Trace, RetrievedChunk


def save_trace(trace: Trace):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO traces (
        trace_id,
        query,
        retrieved_chunks,
        prompt,
        response,
        latency,
        timestamp,
        model_name
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trace.trace_id,
        trace.query,
        json.dumps([chunk.dict() for chunk in trace.retrieved_chunks]),
        trace.prompt,
        trace.response,
        trace.latency,
        trace.timestamp,
        trace.model_name
    ))

    conn.commit()
    conn.close()


def get_traces():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM traces
    ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    traces = []

    for row in rows:

        trace = Trace(
            trace_id=row["trace_id"],
            query=row["query"],
            retrieved_chunks=[
                RetrievedChunk(**chunk)
                for chunk in json.loads(row["retrieved_chunks"])
            ],
            prompt=row["prompt"],
            response=row["response"],
            latency=row["latency"],
            timestamp=row["timestamp"],
            model_name=row["model_name"]
        )

        traces.append(trace)

    return traces


def get_trace_by_id(trace_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM traces
    WHERE trace_id = ?
    """, (trace_id,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {"error": "Trace not found"}

    return Trace(
        trace_id=row["trace_id"],
        query=row["query"],
        retrieved_chunks=[
            RetrievedChunk(**chunk)
            for chunk in json.loads(row["retrieved_chunks"])
        ],
        prompt=row["prompt"],
        response=row["response"],
        latency=row["latency"],
        timestamp=row["timestamp"],
        model_name=row["model_name"]
    )
