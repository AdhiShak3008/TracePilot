import time
from datetime import datetime

from app.retrieval.retriever import retrieve_chunks
from app.models.trace import Trace, RetrievedChunk
from app.tracing.trace_manager import save_trace


def run_rag_pipeline(
    query: str,
    parent_trace_id: str | None = None
):

    start_time = time.time()

    chunks = retrieve_chunks(query)

    avg_score = round(
        sum(chunk["score"] for chunk in chunks) / len(chunks),
        2
    )

    if avg_score >= 0.6:
        retrieval_quality = "good"
    elif avg_score >= 0.4:
        retrieval_quality = "moderate"
    else:
        retrieval_quality = "poor"

    context = "\n".join([chunk["text"] for chunk in chunks])

    prompt = f"""
    Context:
    {context}

    Question:
    {query}
    """

    from app.core.llm import generate_response

    response = generate_response(prompt)
    latency = round((time.time() - start_time) * 1000, 2)

    response_length = len(response.split())
    chunk_count = len(chunks)

    trace = Trace(
        trace_id=Trace.create_id(),
        query=query,
        retrieved_chunks=[RetrievedChunk(**chunk) for chunk in chunks],
        prompt=prompt,
        response=response,
        latency=latency,
        timestamp=datetime.utcnow(),
        model_name="llama-3.1-8b-instant",
        retrieval_score_avg=avg_score,
        response_length=response_length,
        chunk_count=chunk_count,
        parent_trace_id=parent_trace_id,
        retrieval_quality=retrieval_quality
    )

    save_trace(trace)

    return trace
