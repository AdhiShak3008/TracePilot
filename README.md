# TracePilot

A RAG (Retrieval-Augmented Generation) observability platform. TracePilot traces every query through your pipeline — retrieval, prompting, LLM response — and stores it for inspection, replay, and evaluation.

---

## What It Does

- Accepts a natural language query via REST API
- Retrieves relevant chunks from a local knowledge base using keyword scoring
- Builds a prompt and generates a response via an LLM (Groq / llama-3.1-8b-instant)
- Records the full trace: query, retrieved chunks, prompt, response, latency, model, timestamp
- Persists traces to SQLite
- Exposes endpoints to fetch and replay any trace

---

## Project Structure

```
TracePilot/
├── backend/
│   ├── app/
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

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ask` | Run a query through the RAG pipeline |
| GET | `/traces` | Fetch all traces (newest first) |
| GET | `/traces/{trace_id}` | Fetch a single trace by ID |
| POST | `/traces/{trace_id}/replay` | Replay a trace with the same query |

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

## Example Request

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the best time to visit Tawang?"}'
```

---

## Tech Stack

- **Backend** — FastAPI, SQLite, Pydantic
- **LLM** — Groq API (llama-3.1-8b-instant)
- **Retrieval** — Keyword scoring (Counter-based BM25-lite)
- **Frontend** — React + Vite (in progress)
- **Tracing** — Custom trace manager with SQLite persistence
