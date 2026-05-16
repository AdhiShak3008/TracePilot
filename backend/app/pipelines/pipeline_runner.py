import uuid
from datetime import datetime

from app.retrieval.retriever import retrieve_chunks
from app.pipelines.prompt_builder import build_prompt
from app.core.llm import generate_response
from app.evaluation.evaluator import Evaluator
from app.tracing.spans import ExecutionSpan
from app.tracing.trace_manager import save_trace
from app.models.trace import Trace, RetrievedChunk


class PipelineRunner:

    def __init__(self):

        self.evaluator = Evaluator()

    def run(self, query, parent_trace_id=None):

        trace_id = str(uuid.uuid4())

        spans = []

        start_time = datetime.utcnow()

        # --- Retrieval Span ---

        retrieval_span = ExecutionSpan(
            trace_id=trace_id,
            span_type="retrieval",
            input_payload={"query": query}
        )

        chunks = retrieve_chunks(query)

        retrieval_span.finish({"retrieved_count": len(chunks)})

        spans.append(retrieval_span)

        # --- Metrics ---

        avg_score = (
            round(sum(chunk["score"] for chunk in chunks) / len(chunks), 2)
            if chunks else 0
        )

        top_score = chunks[0]["score"] if chunks else 0

        if top_score >= 0.5:
            retrieval_quality = "good"
        elif top_score >= 0.3:
            retrieval_quality = "moderate"
        else:
            retrieval_quality = "poor"

        # --- Prompt Span ---

        prompt_span = ExecutionSpan(
            trace_id=trace_id,
            span_type="prompt_build"
        )

        prompt = build_prompt(query, chunks)

        prompt_span.finish({"prompt_length": len(prompt)})

        spans.append(prompt_span)

        # --- Generation Span ---

        generation_span = ExecutionSpan(
            trace_id=trace_id,
            span_type="generation"
        )

        response = generate_response(prompt)

        generation_span.finish({"response_length": len(response.split())})

        spans.append(generation_span)

        # --- Evaluation Span ---

        evaluation_span = ExecutionSpan(
            trace_id=trace_id,
            span_type="evaluation"
        )

        evaluation = self.evaluator.evaluate(query, response, chunks)

        evaluation_span.finish(evaluation)

        spans.append(evaluation_span)

        # --- Latency ---

        latency = round(
            (datetime.utcnow() - start_time).total_seconds() * 1000, 2
        )

        # --- Failure Classification ---

        failure_types = []

        if not chunks:
            failure_types.append("retrieval_empty")

        if retrieval_quality == "poor":
            failure_types.append("poor_retrieval")

        if not evaluation["grounded"]:
            failure_types.append("ungrounded_response")

        if evaluation["abstained"]:
            failure_types.append("insufficient_context")

        elif evaluation["hallucination_score"] > 0.8:
            failure_types.append("hallucination")

            if evaluation["grounded"]:
                failure_types.append("retrieval_amplified_hallucination")

        if latency > 2000:
            failure_types.append("high_latency")

        # --- Span Summaries ---

        span_summaries = [
            {
                "span_type": span.span_type,
                "duration_ms": span.duration_ms,
                "status": span.status,
            }
            for span in spans
        ]

        # --- Trace Construction ---

        trace = Trace(
            trace_id=trace_id,
            query=query,
            retrieved_chunks=[RetrievedChunk(**chunk) for chunk in chunks],
            prompt=prompt,
            response=response,
            latency=latency,
            timestamp=datetime.utcnow(),
            model_name="llama-3.1-8b-instant",
            retrieval_score_avg=avg_score,
            response_length=len(response.split()),
            chunk_count=len(chunks),
            parent_trace_id=parent_trace_id,
            retrieval_quality=retrieval_quality,
            grounded=evaluation["grounded"],
            top_retrieval_score=top_score,
            spans=span_summaries,
            failure_types=failure_types,
        )

        save_trace(trace)

        return {
            "trace_id": trace_id,
            "retrieval": {
                "avg_score": avg_score,
                "top_score": top_score,
                "retrieval_quality": retrieval_quality,
            },
            "response": response,
            "evaluation": evaluation,
            "failure_types": failure_types,
            "spans": span_summaries,
        }
