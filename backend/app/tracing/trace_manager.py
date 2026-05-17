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
        model_name,
        retrieval_score_avg,
        response_length,
        chunk_count,
        parent_trace_id,
        retrieval_quality,
        grounded,
        top_retrieval_score,
        spans,
        failure_types,
        prompt_mode
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trace.trace_id,
        trace.query,
        json.dumps([chunk.dict() for chunk in trace.retrieved_chunks]),
        trace.prompt,
        trace.response,
        trace.latency,
        str(trace.timestamp),
        trace.model_name,
        trace.retrieval_score_avg,
        trace.response_length,
        trace.chunk_count,
        trace.parent_trace_id,
        trace.retrieval_quality,
        trace.grounded,
        trace.top_retrieval_score,
        json.dumps(trace.spans),
        json.dumps(trace.failure_types),
        trace.prompt_mode
    ))

    conn.commit()
    conn.close()


def get_traces(retrieval_quality=None):

    conn = get_connection()
    cursor = conn.cursor()

    if retrieval_quality:

        cursor.execute(
            """
            SELECT * FROM traces
            WHERE retrieval_quality = ?
            ORDER BY timestamp DESC
            """,
            (retrieval_quality,)
        )

    else:

        cursor.execute(
            """
            SELECT * FROM traces
            ORDER BY timestamp DESC
            """
        )

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
            model_name=row["model_name"],
            retrieval_score_avg=row["retrieval_score_avg"],
            response_length=row["response_length"],
            chunk_count=row["chunk_count"],
            parent_trace_id=row["parent_trace_id"],
            retrieval_quality=row["retrieval_quality"],
            grounded=row["grounded"],
            top_retrieval_score=row["top_retrieval_score"],
            spans=json.loads(row["spans"] or "[]"),
            failure_types=json.loads(row["failure_types"] or "[]"),
            prompt_mode=row["prompt_mode"] or "strict"
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
        model_name=row["model_name"],
        retrieval_score_avg=row["retrieval_score_avg"],
        response_length=row["response_length"],
        chunk_count=row["chunk_count"],
        parent_trace_id=row["parent_trace_id"],
        retrieval_quality=row["retrieval_quality"],
        grounded=row["grounded"],
        top_retrieval_score=row["top_retrieval_score"],
        spans=json.loads(row["spans"] or "[]"),
        failure_types=json.loads(row["failure_types"] or "[]"),
        prompt_mode=row["prompt_mode"] or "strict"
    )


def get_trace(trace_id: str) -> dict | None:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM traces
    WHERE trace_id = ?
    """, (trace_id,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "trace_id": row["trace_id"],
        "query": row["query"],
        "retrieved_chunks": json.loads(row["retrieved_chunks"]),
        "prompt": row["prompt"],
        "response": row["response"],
        "latency": row["latency"],
        "timestamp": row["timestamp"],
        "model_name": row["model_name"],
        "retrieval_score_avg": row["retrieval_score_avg"],
        "response_length": row["response_length"],
        "chunk_count": row["chunk_count"],
        "parent_trace_id": row["parent_trace_id"],
        "retrieval_quality": row["retrieval_quality"],
        "grounded": row["grounded"],
        "top_retrieval_score": row["top_retrieval_score"],
        "spans": json.loads(row["spans"] or "[]"),
        "failure_types": json.loads(row["failure_types"] or "[]")
    }
