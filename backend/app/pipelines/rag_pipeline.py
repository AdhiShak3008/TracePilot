import time
from datetime import datetime

from app.retrieval.retriever import retrieve_chunks
from app.models.trace import Trace, RetrievedChunk
from app.tracing.trace_manager import save_trace


def run_rag_pipeline(query: str):

    start_time = time.time()

    chunks = retrieve_chunks(query)

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

    trace = Trace(
        trace_id=Trace.create_id(),
        query=query,
        retrieved_chunks=[RetrievedChunk(**chunk) for chunk in chunks],
        prompt=prompt,
        response=response,
        latency=latency,
        timestamp=datetime.utcnow().isoformat(),
    )

    save_trace(trace)

    return trace
