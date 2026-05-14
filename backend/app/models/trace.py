from pydantic import BaseModel
from typing import List
from uuid import uuid4
from datetime import datetime


class RetrievedChunk(BaseModel):
    text: str
    score: float


class Trace(BaseModel):
    trace_id: str
    query: str
    retrieved_chunks: List[RetrievedChunk]
    prompt: str
    response: str
    latency: float
    timestamp: str

    @staticmethod
    def create_id():
        return str(uuid4())
