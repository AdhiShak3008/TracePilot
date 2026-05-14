from fastapi import FastAPI
from pydantic import BaseModel

from app.pipelines.rag_pipeline import run_rag_pipeline
from app.tracing.trace_manager import get_traces, get_trace_by_id

app = FastAPI()


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
