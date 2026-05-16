import json
from fastapi import APIRouter
from app.tracing.trace_manager import get_traces, get_trace_by_id

router = APIRouter(prefix="/traces", tags=["traces"])


def serialize_trace(trace):
    data = trace.dict()
    if isinstance(data.get("retrieved_chunks"), str):
        data["retrieved_chunks"] = json.loads(data["retrieved_chunks"])
    if isinstance(data.get("spans"), str):
        data["spans"] = json.loads(data["spans"])
    if isinstance(data.get("failure_types"), str):
        data["failure_types"] = json.loads(data["failure_types"])
    return data


@router.get("/")
def fetch_traces(retrieval_quality: str | None = None):
    return [serialize_trace(t) for t in get_traces(retrieval_quality)]


@router.get("/{trace_id}")
def fetch_trace(trace_id: str):
    trace = get_trace_by_id(trace_id)
    if isinstance(trace, dict):
        return trace
    return serialize_trace(trace)
