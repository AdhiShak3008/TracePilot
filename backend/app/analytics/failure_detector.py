from app.tracing.trace_manager import get_traces


def detect_failures():

    traces = get_traces()

    failures = []

    for trace in traces:

        reasons = []

        if trace.retrieval_quality == "poor":
            reasons.append("poor_retrieval")

        if trace.latency > 2000:
            reasons.append("high_latency")

        if reasons:

            failures.append({
                "trace_id": trace.trace_id,
                "query": trace.query,
                "reasons": reasons,
                "latency": trace.latency,
                "retrieval_quality": trace.retrieval_quality
            })

    return failures
