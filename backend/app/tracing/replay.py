from app.pipelines.pipeline_runner import PipelineRunner
from app.tracing.trace_manager import get_trace


def replay_trace(trace_id: str):

    original_trace = get_trace(trace_id)

    if not original_trace:
        return {"error": "Trace not found"}

    runner = PipelineRunner()

    return runner.run(
        query=original_trace["query"],
        parent_trace_id=trace_id
    )
