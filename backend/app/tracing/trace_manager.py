traces = []


def save_trace(trace):
    traces.append(trace)


def get_traces():
    return traces


def get_trace_by_id(trace_id):
    for trace in traces:
        if trace.trace_id == trace_id:
            return trace
    return {"error": "Trace not found"}
