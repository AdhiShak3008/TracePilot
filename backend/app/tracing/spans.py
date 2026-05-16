from datetime import datetime
import uuid


class ExecutionSpan:

    def __init__(
        self,
        trace_id,
        span_type,
        input_payload=None,
        metadata=None,
        parent_span_id=None
    ):

        self.span_id = str(uuid.uuid4())

        self.trace_id = trace_id

        self.parent_span_id = parent_span_id

        self.span_type = span_type

        self.started_at = datetime.utcnow()

        self.ended_at = None

        self.duration_ms = None

        self.input_payload = input_payload or {}

        self.output_payload = {}

        self.metadata = metadata or {}

        self.status = "running"

    def finish(self, output_payload=None):

        self.ended_at = datetime.utcnow()

        self.duration_ms = round(
            (self.ended_at - self.started_at).total_seconds() * 1000,
            3
        )

        self.output_payload = output_payload or {}

        self.status = "completed"

    def fail(self, error_message):

        self.ended_at = datetime.utcnow()

        self.duration_ms = round(
            (self.ended_at - self.started_at).total_seconds() * 1000,
            3
        )

        self.status = "failed"

        self.metadata["error"] = error_message
