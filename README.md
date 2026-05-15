# TracePilot

A RAG (Retrieval-Augmented Generation) observability platform. TracePilot traces every query through your pipeline — retrieval, prompting, LLM response — and stores it for inspection, replay, and evaluation.

---

## What It Does

- Accepts a natural language query via REST API
- Retrieves relevant chunks from a local knowledge base using keyword scoring
- Assigns each chunk a `chunk_id` and `rank` for retrieval provenance
- Builds a prompt and generates a response via an LLM (Groq / llama-3.1-8b-instant)
- Classifies retrieval quality as `good`, `moderate`, or `poor` based on top chunk score
- Checks groundedness via stopword-filtered word overlap between response and retrieved chunks
- Records the full trace: query, retrieved chunks, prompt, response, latency, model, timestamp, and metrics
- Persists traces to SQLite
- Exposes endpoints to fetch, replay, and compare traces
- Replay traces are linked to their origin via `parent_trace_id`
- Detects failure patterns via the analytics layer

---

## Project Structure

```
TracePilot/
├── backend/
│   ├── app/
│   │   ├── analytics/          # Failure detection and analytics
│   │   ├── api/routes/         # FastAPI route definitions
│   │   ├── core/               # Config, logging, telemetry, LLM client
│   │   ├── db/                 # SQLite connection and schema init
│   │   ├── evaluation/         # Hallucination, faithfulness, groundedness scorers
│   │   ├── experiments/        # Benchmark runner, dataset loader, comparisons
│   │   ├── models/             # Pydantic models (Trace, RetrievedChunk)
│   │   ├── pipelines/          # RAG pipeline, prompt builder
│   │   ├── retrieval/          # Retriever, reranker, embeddings, chunking
│   │   ├── tracing/            # Trace manager, spans, replay, metrics
│   │   ├── workers/            # Ingestion and evaluation workers
│   │   └── main.py             # FastAPI app entry point
│   ├── data/
│   │   └── knowledge_base.txt  # Local knowledge base
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/              # Dashboard, TraceExplorer, Experiments, RetrievalAnalytics
│   │   ├── components/         # TraceGraph, MetricsCard, RetrievalTable, PromptViewer
│   │   ├── services/api.js     # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

---

## Data Models

### RetrievedChunk
| Field | Type | Description |
|---|---|---|
| chunk_id | str | Unique chunk identifier (chunk_0, chunk_1, ...) |
| text | str | Chunk content |
| score | float | Keyword relevance score |
| rank | int | Retrieval ranking position |

### Trace
| Field | Type | Description |
|---|---|---|
| trace_id | str | UUID |
| query | str | Original user query |
| retrieved_chunks | List[RetrievedChunk] | Top-k retrieved chunks |
| prompt | str | Full prompt sent to LLM |
| response | str | LLM response |
| latency | float | End-to-end latency in ms |
| timestamp | datetime | UTC time of the trace |
| model_name | str | LLM model used |
| retrieval_score_avg | float | Average keyword score across retrieved chunks |
| response_length | int | Word count of the LLM response |
| chunk_count | int | Number of chunks retrieved |
| parent_trace_id | str or None | ID of the original trace if this is a replay |
| retrieval_quality | str | Quality label based on top chunk score: `good`, `moderate`, or `poor` |
| grounded | bool | Whether the response overlaps meaningfully with retrieved chunks |

---

## Retrieval Quality Heuristic

Based on the top-ranked chunk's score:

| Top Score | Label |
|---|---|
| >= 0.5 | good |
| >= 0.3 | moderate |
| < 0.3 | poor |

---

## Groundedness Heuristic

Stopword-filtered word overlap between the response and each retrieved chunk. A trace is marked `grounded = true` if at least 2 non-stopword words from any chunk appear in the response.

Stopwords filtered: `the`, `is`, `a`, `an`, `to`, `of`, `and`, `in`, `on`, `for`, `what`, `best`, `how`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ask` | Run a query through the RAG pipeline |
| GET | `/traces` | Fetch all traces (newest first) |
| GET | `/traces?retrieval_quality=good` | Filter traces by retrieval quality |
| GET | `/traces/compare?trace_id_1=X&trace_id_2=Y` | Compare two traces side by side |
| GET | `/traces/{trace_id}` | Fetch a single trace by ID |
| POST | `/traces/{trace_id}/replay` | Replay a trace with the same query |
| GET | `/analytics/failures` | Detect traces with poor retrieval or high latency |

### Compare Response Shape

```json
{
  "trace_1": { "trace_id", "model_name", "latency", "retrieval_score_avg", "response_length", "chunk_count" },
  "trace_2": { "trace_id", "model_name", "latency", "retrieval_score_avg", "response_length", "chunk_count" },
  "differences": {
    "latency_delta": float,
    "retrieval_score_delta": float,
    "response_length_delta": int,
    "response_changed": bool
  }
}
```

### Failure Detection Response Shape

```json
[
  {
    "trace_id": "...",
    "query": "...",
    "reasons": ["poor_retrieval", "high_latency"],
    "latency": 2500.0,
    "retrieval_quality": "poor"
  }
]
```

Failure conditions:
- `poor_retrieval` — retrieval quality is `poor`
- `high_latency` — latency exceeds 2000ms

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/TracePilot.git
cd TracePilot/backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in `backend/`:

```
GROQ_API_KEY=your_api_key_here
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Example Requests

```bash
# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the best time to visit Tawang?"}'

# Fetch all traces
curl http://localhost:8000/traces

# Filter by retrieval quality
curl "http://localhost:8000/traces?retrieval_quality=poor"

# Fetch a single trace
curl http://localhost:8000/traces/<trace_id>

# Replay a trace
curl -X POST http://localhost:8000/traces/<trace_id>/replay

# Compare two traces
curl "http://localhost:8000/traces/compare?trace_id_1=<id1>&trace_id_2=<id2>"

# Detect failures
curl http://localhost:8000/analytics/failures
```

---

## Schema Migration Note

This project uses SQLite with manual schema management. If you add new fields to the `Trace` model, delete `tracepilot.db` and restart the server — `init_db()` will recreate the table with the updated schema.

---

## Tech Stack

- **Backend** — FastAPI, SQLite, Pydantic
- **LLM** — Groq API (llama-3.1-8b-instant)
- **Retrieval** — Keyword scoring (Counter-based BM25-lite)
- **Analytics** — Custom failure detection layer
- **Frontend** — React + Vite (in progress)
- **Tracing** — Custom trace manager with SQLite persistence
