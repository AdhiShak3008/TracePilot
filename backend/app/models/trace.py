from pydantic import BaseModel
from typing import List
from uuid import uuid4
from datetime import datetime


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    score: float
    rank: int


class Trace(BaseModel):
    trace_id: str
    query: str
    retrieved_chunks: List[RetrievedChunk]
    prompt: str
    response: str
    latency: float
    timestamp: datetime
    model_name: str
    retrieval_score_avg: float
    response_length: int
    chunk_count: int

    @staticmethod
    def create_id():
        return str(uuid4())
