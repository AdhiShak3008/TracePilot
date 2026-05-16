import { useEffect, useState } from "react";
import api from "../services/api";

const qualityColor = {
    good: "#4caf50",
    moderate: "#ff9800",
    poor: "#f44336"
};

export default function TraceExplorer() {
    const [traces, setTraces] = useState([]);
    const [selectedTrace, setSelectedTrace] = useState(null);
    const [selectedId, setSelectedId] = useState(null);

    useEffect(() => {
        api.get("/traces").then(r => setTraces(r.data));
    }, []);

    async function loadTrace(traceId) {
        setSelectedId(traceId);
        const r = await api.get(`/traces/${traceId}`);
        setSelectedTrace(r.data);
    }

    async function replayTrace(traceId) {
        await api.post(`/traces/${traceId}/replay`);
        const r = await api.get("/traces");
        setTraces(r.data);
    }

    return (
        <div style={{ display: "flex", height: "100vh", background: "#0f0f0f", color: "#e0e0e0", fontFamily: "monospace" }}>

            {/* SIDEBAR */}
            <div style={{ width: "32%", borderRight: "1px solid #2a2a2a", overflowY: "auto", padding: "1rem" }}>
                <h2 style={{ marginTop: 0, color: "#fff", fontSize: "1.1rem", letterSpacing: "0.05em" }}>
                    TRACES <span style={{ color: "#555", fontWeight: "normal" }}>({traces.length})</span>
                </h2>

                {traces.map(trace => (
                    <div
                        key={trace.trace_id}
                        onClick={() => loadTrace(trace.trace_id)}
                        style={{
                            padding: "0.75rem",
                            marginBottom: "0.5rem",
                            border: `1px solid ${selectedId === trace.trace_id ? "#555" : "#222"}`,
                            background: selectedId === trace.trace_id ? "#1a1a1a" : "transparent",
                            cursor: "pointer",
                            borderRadius: "4px"
                        }}
                    >
                        <p style={{ margin: "0 0 0.4rem", fontSize: "0.85rem", color: "#ccc" }}>
                            {trace.query}
                        </p>
                        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                            <Tag color={qualityColor[trace.retrieval_quality]}>
                                {trace.retrieval_quality}
                            </Tag>
                            {trace.parent_trace_id && <Tag color="#7c4dff">replay</Tag>}
                        </div>
                    </div>
                ))}
            </div>

            {/* RIGHT PANEL */}
            <div style={{ flex: 1, overflowY: "auto", padding: "2rem" }}>
                {!selectedTrace ? (
                    <p style={{ color: "#444" }}>← Select a trace to inspect</p>
                ) : (
                    <div>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                            <h1 style={{ margin: "0 0 0.25rem", fontSize: "1.1rem", color: "#fff" }}>
                                {selectedTrace.query}
                            </h1>
                            <button
                                onClick={() => replayTrace(selectedTrace.trace_id)}
                                style={{
                                    background: "#1e1e1e", color: "#aaa", border: "1px solid #333",
                                    padding: "0.4rem 0.9rem", cursor: "pointer", borderRadius: "4px",
                                    fontSize: "0.8rem", flexShrink: 0, marginLeft: "1rem"
                                }}
                            >
                                ↺ Replay
                            </button>
                        </div>

                        <div style={{ display: "flex", gap: "0.5rem", margin: "0.75rem 0 1.5rem", flexWrap: "wrap" }}>
                            <Tag color={qualityColor[selectedTrace.retrieval_quality]}>
                                retrieval: {selectedTrace.retrieval_quality}
                            </Tag>
                            <Tag color={selectedTrace.grounded ? "#4caf50" : "#f44336"}>
                                {selectedTrace.grounded ? "grounded" : "not grounded"}
                            </Tag>
                            <Tag color="#555">{selectedTrace.model_name}</Tag>
                            <Tag color="#555">{selectedTrace.latency?.toFixed(0)} ms</Tag>
                            {selectedTrace.parent_trace_id && (
                                <Tag color="#7c4dff">replay of {selectedTrace.parent_trace_id.slice(0, 8)}…</Tag>
                            )}
                        </div>

                        <Section title="Response">
                            <p style={{ lineHeight: 1.7, color: "#ccc" }}>{selectedTrace.response}</p>
                        </Section>

                        <Section title="Retrieved Chunks">
                            {selectedTrace.retrieved_chunks?.map(chunk => (
                                <div key={chunk.chunk_id} style={{
                                    background: "#141414", border: "1px solid #222",
                                    borderRadius: "4px", padding: "0.75rem", marginBottom: "0.5rem"
                                }}>
                                    <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.4rem" }}>
                                        <Tag color="#333">{chunk.chunk_id}</Tag>
                                        <Tag color="#333">rank {chunk.rank}</Tag>
                                        <Tag color="#333">score {chunk.score?.toFixed(3)}</Tag>
                                    </div>
                                    <p style={{ margin: 0, fontSize: "0.82rem", color: "#aaa", lineHeight: 1.6 }}>
                                        {chunk.text}
                                    </p>
                                </div>
                            ))}
                        </Section>

                        <Section title="Metrics">
                            <pre style={{ margin: 0, color: "#aaa", fontSize: "0.82rem" }}>
                                {JSON.stringify({
                                    retrieval_score_avg: selectedTrace.retrieval_score_avg,
                                    response_length: selectedTrace.response_length,
                                    chunk_count: selectedTrace.chunk_count,
                                    timestamp: selectedTrace.timestamp
                                }, null, 2)}
                            </pre>
                        </Section>
                    </div>
                )}
            </div>
        </div>
    );
}

function Tag({ color, children }) {
    return (
        <span style={{
            background: color + "22", color, border: `1px solid ${color}55`,
            borderRadius: "3px", padding: "0.1rem 0.45rem", fontSize: "0.72rem"
        }}>
            {children}
        </span>
    );
}

function Section({ title, children }) {
    return (
        <div style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ margin: "0 0 0.6rem", fontSize: "0.78rem", color: "#555", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                {title}
            </h3>
            {children}
        </div>
    );
}
