from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db.database import init_db
from app.pipelines.rag_pipeline import run_rag_pipeline
from app.tracing.trace_manager import get_traces, get_trace_by_id

app = FastAPI()

init_db()


class QueryRequest(BaseModel):
    query: str


@app.post("/ask")
def ask_question(request: QueryRequest):

    trace = run_rag_pipeline(request.query)

    return trace


@app.get("/traces")
def get_all_traces():

    return get_traces()


@app.get("/traces/{trace_id}")
def fetch_trace(trace_id: str):

    return get_trace_by_id(trace_id)


@app.post("/traces/{trace_id}/replay")
def replay_trace(trace_id: str):

    trace = get_trace_by_id(trace_id)

    if isinstance(trace, dict):
        raise HTTPException(status_code=404, detail="Trace not found")

    replayed_trace = run_rag_pipeline(trace.query)

    return {
        "original_trace_id": trace.trace_id,
        "replayed_trace_id": replayed_trace.trace_id,
        "original_response": trace.response,
        "replayed_response": replayed_trace.response,
    }
