from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db.database import init_db
from app.pipelines.rag_pipeline import run_rag_pipeline
from app.tracing.trace_manager import get_traces, get_trace_by_id
from app.analytics.failure_detector import detect_failures

app = FastAPI()

init_db()


class QueryRequest(BaseModel):
    query: str


@app.post("/ask")
def ask_question(request: QueryRequest):

    trace = run_rag_pipeline(request.query)

    return trace


@app.get("/analytics/failures")
def get_failures():

    return detect_failures()


@app.get("/traces")
def get_all_traces(
    retrieval_quality: str | None = None
):

    return get_traces(retrieval_quality)


@app.get("/traces/compare")
def compare_traces(trace_id_1: str, trace_id_2: str):

    trace_1 = get_trace_by_id(trace_id_1)
    trace_2 = get_trace_by_id(trace_id_2)

    if isinstance(trace_1, dict):
        raise HTTPException(status_code=404, detail="First trace not found")

    if isinstance(trace_2, dict):
        raise HTTPException(status_code=404, detail="Second trace not found")

    return {
        "trace_1": {
            "trace_id": trace_1.trace_id,
            "model_name": trace_1.model_name,
            "latency": trace_1.latency,
            "retrieval_score_avg": trace_1.retrieval_score_avg,
            "response_length": trace_1.response_length,
            "chunk_count": trace_1.chunk_count
        },
        "trace_2": {
            "trace_id": trace_2.trace_id,
            "model_name": trace_2.model_name,
            "latency": trace_2.latency,
            "retrieval_score_avg": trace_2.retrieval_score_avg,
            "response_length": trace_2.response_length,
            "chunk_count": trace_2.chunk_count
        },
        "differences": {
            "latency_delta": round(trace_2.latency - trace_1.latency, 2),
            "retrieval_score_delta": round(trace_2.retrieval_score_avg - trace_1.retrieval_score_avg, 2),
            "response_length_delta": trace_2.response_length - trace_1.response_length,
            "response_changed": trace_1.response != trace_2.response
        }
    }


@app.get("/traces/{trace_id}")
def fetch_trace(trace_id: str):

    return get_trace_by_id(trace_id)


@app.post("/traces/{trace_id}/replay")
def replay_trace(trace_id: str):

    trace = get_trace_by_id(trace_id)

    if isinstance(trace, dict):
        raise HTTPException(status_code=404, detail="Trace not found")

    replayed_trace = run_rag_pipeline(
        trace.query,
        parent_trace_id=trace.trace_id
    )

    return {
        "original_trace_id": trace.trace_id,
        "replayed_trace_id": replayed_trace.trace_id,
        "original_response": trace.response,
        "replayed_response": replayed_trace.response,
    }
