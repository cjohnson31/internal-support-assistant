# Internal Support Assistant

A RAG-powered support agent that answers employee questions by retrieving information from a knowledge base and ticket history, generating grounded answers with inline citations, and refusing when it doesn't have enough information rather than hallucinating.

Built as a portfolio project demonstrating end-to-end LLM engineering: retrieval, generation, Slack integration, and — most importantly — an **automated eval harness** for measuring answer quality.

## Eval Results

| Metric | Score |
|--------|-------|
| Retrieval Hit-Rate@5 | **100%** |
| Refusal Accuracy (overall) | **100%** |
| Avg Answer Correctness (1–5) | **4.96** |
| Avg Groundedness (1–5) | **4.93** |

*38 test cases (28 answerable + 10 out-of-scope). Correctness and groundedness scored by LLM-as-judge. Full reports in `evals/reports/`.*

## Architecture

```
┌──────────────────────────────┐
│  Web UI / Slack / CLI        │
│  (user query + API key)      │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐     ┌───────────────┐
│  Agent Pipeline              │────▶│  LLM (Claude) │
│  retrieve → gate → generate  │     └───────────────┘
└──────────────┬───────────────┘
               │ retrieve
        ┌──────▼───────┐
        │  Vector Store │
        │  (Chroma)     │
        └──────┬───────┘
               │ embedded
   ┌───────────▼───────────┐
   │  Knowledge Base Docs   │
   │  + Ticket History      │
   └───────────────────────┘
```

**RAG Pipeline:**
1. **Ingest** — Markdown docs and ticket history are chunked (with contextual prefixes for better retrieval), embedded via `sentence-transformers`, and stored in Chroma
2. **Retrieve** — User query is embedded and matched against stored chunks via cosine similarity
3. **Confidence Gate** — If the top retrieval score is below threshold, refuse immediately (no LLM call)
4. **Generate** — Retrieved chunks are assembled into a prompt; Claude generates a grounded answer with inline `[source_id]` citations
5. **LLM Refusal Gate** — Even if retrieval passes, the model is instructed to refuse if context is insufficient (two-layer defense)

**Eval Harness:**
- YAML test set with expected facts, expected sources, and refusal labels
- Four automated metrics: retrieval hit-rate, refusal accuracy, answer correctness (LLM-as-judge), groundedness (LLM-as-judge)
- Dated reports for tracking quality across prompt/retrieval changes

## Quick Start

### Prerequisites
- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)
- A [Slack app](https://api.slack.com/apps) with Socket Mode enabled (if running Slack bot integration)

### Setup

```bash
# Clone and set up
git clone https://github.com/cjohnson31/internal-support-assistant.git
cd internal-support-assistant
python -m venv .venv
source .venv/bin/activate
pip install .

# Configure
cp .env.example .env
# Edit .env with your API keys
```

### Run Locally

```bash
# Ingest the knowledge base into the vector store
python -m src.cli ingest

# Start the web UI (http://localhost:8000)
python -m src.web

# Or ask via CLI
python -m src.cli ask "How do I rotate service account credentials?"

# Or start the Slack bot (requires Slack app setup)
python -m src.slack
```

> **Web UI note:** The web interface requires you to enter your own Anthropic API key.
> Your key is sent directly to the Anthropic API per-request and is never stored.

### Run with Docker (easiest)

```bash
# Build and run — ingests docs, starts web UI at http://localhost:8000
docker compose -f docker/docker-compose.yml up --build
```

No `.env` file needed for the web UI — you enter your API key in the browser.

To also run the Slack bot (requires `.env` with Slack tokens):
```bash
docker compose -f docker/docker-compose.yml --profile slack up --build
```

### Run Evals

```bash
python -m evals.run_evals
```

## Project Structure

```
internal-support-assistant/
├── data/
│   ├── knowledge_base/      # Source docs (markdown)
│   └── tickets/             # Synthetic ticket history (JSON)
├── src/
│   ├── config.py            # Pydantic settings (env-driven)
│   ├── llm.py               # Provider-agnostic LLM + embeddings wrapper
│   ├── ingest/              # Loaders, chunking, embedding, upsert
│   ├── retrieval/           # Vector store search
│   ├── agent/               # Prompt templates, answer generation, refusal gate
│   ├── slack/               # Bolt app (Socket Mode)
│   ├── web/                 # FastAPI web UI (BYOK — bring your own key)
│   └── cli.py               # CLI commands (ingest, ask, search)
├── evals/
│   ├── testset.yaml         # 38 labeled test cases
│   ├── metrics.py           # Retrieval, correctness, groundedness, refusal scoring
│   ├── run_evals.py         # Automated eval runner
│   └── reports/             # Dated eval reports (markdown + JSON)
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

## Tech Stack

- **LLM**: Claude (Anthropic) via official SDK, behind a provider-agnostic wrapper
- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2, 384-dim, runs locally)
- **Vector Store**: Chroma (local, persistent)
- **Web UI**: FastAPI single-page app (BYOK — users provide their own API key)
- **Slack**: Bolt for Python (Socket Mode — no public URL needed)
- **Evals**: LLM-as-judge with separate judge model; YAML test set
- **Config**: pydantic-settings (env-driven)
- **Container**: Docker + Docker Compose

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_API_KEY` | Anthropic API key |
| `LLM_MODEL` | Model for answer generation (default: `claude-haiku-4-5-20251001`) |
| `EMBEDDING_MODEL` | Sentence-transformers model (default: `all-MiniLM-L6-v2`) |
| `JUDGE_MODEL` | Model for eval scoring (default: `claude-haiku-4-5-20251001`) |
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth Token |
| `SLACK_APP_TOKEN` | Slack App-Level Token (Socket Mode) |
| `CONFIDENCE_THRESHOLD` | Minimum retrieval score to attempt answering (default: `0.3`) |
| `RETRIEVAL_TOP_K` | Number of chunks to retrieve (default: `5`) |

## Key Design Decisions

- **Two-layer refusal**: A retrieval confidence gate catches obvious misses cheaply (no LLM call); the LLM prompt catches borderline cases where retrieved context doesn't actually answer the question
- **Contextual chunk prefixes**: Each chunk is prefixed with its document title and section heading, improving embedding quality for tables and lists
- **Cheap models by default**: Uses Haiku-tier models for both generation and eval judging — the full build costs a few dollars
- **No framework lock-in**: The RAG pipeline is built from primitives (embed, retrieve, prompt, generate) rather than hidden behind LangChain/LlamaIndex, making every step inspectable and debuggable
