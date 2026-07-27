# Deployment Guide — Jianuo AI Assistant (rag_basics)

## Services

### FastAPI Backend
- **Name**: ai-immigration-assistant
- **URL**: https://ai-immigration-assistant.onrender.com
- **Provider**: Render Web Service (free tier)
- **Region**: Oregon
- **Runtime**: Python 3.13

### Streamlit UI
- **Name**: ai-immigration-assistant-ui
- **URL**: https://ai-immigration-assistant-ui.onrender.com
- **Provider**: Render Web Service (free tier)
- **Region**: Oregon
- **Runtime**: Python 3.13

## External Dependencies

- **Pinecone**: Serverless index `jianuo-dev-v1` (AWS us-east-1, 1536-dim, cosine)
- **OpenAI**: `text-embedding-3-small` for embeddings, `gpt-4o-mini` for generation
- **Cohere**: `rerank-v3.5` for cross-encoder reranking

## FastAPI Configuration

- **GitHub Source**: https://github.com/ZihaoWang617/ai-engineer-learning
- **Branch**: main
- **Root Directory**: `./`
- **Build Command**: `pip install -r requirements.txt && pip install -e .`
- **Start Command**: `uvicorn rag_basics.app:app --host 0.0.0.0 --port 8000`
- **Auto-Deploy**: On Commit

### Required Environment Variables

| Key | Purpose |
|-----|---------|
| `OPENAI_API_KEY` | Embeddings + LLM generation |
| `COHERE_API_KEY` | Reranking |
| `PINECONE_API_KEY` | Vector store queries |
| `PYTHON_VERSION` | Set to `3.13` — see Known Issues #2 |

## Streamlit Configuration

- **GitHub Source**: Same repo, same branch
- **Root Directory**: `./`
- **Build Command**: `pip install -r requirements.txt && pip install -e .`
- **Start Command**: `streamlit run rag_basics/streamlit_app.py --server.port 8000 --server.address 0.0.0.0`
- **Auto-Deploy**: On Commit

### Required Environment Variables

| Key | Purpose |
|-----|---------|
| `API_URL` | Points to FastAPI backend URL (`https://ai-immigration-assistant.onrender.com`) |
| `PYTHON_VERSION` | Set to `3.13` |

## Known Issues

### 1. Knowledge base is 3 chunks — hybrid + rerank unvalidated at scale

The Pinecone index currently holds 3 chunks. Hybrid retrieval (Pinecone vector + BM25) and Cohere reranking are wired end-to-end and work correctly on this dataset, but at 3 chunks any retrieval method will look the same — there isn't enough content for BM25 and vector search to disagree meaningfully, and rerank has nothing to reorder.

**Trade-off:** Shipped the architecture before the content. This was deliberate — proving the pipeline end-to-end de-risks the harder problem (integration, deploy) before the softer one (knowledge base curation).

**Action:** Expand `knowledge_base.txt` before internal beta. Target size: enough chunks that hybrid and pure-vector return visibly different top-k on realistic queries.

---

### 2. Python version must be pinned to 3.13 (Render defaults to 3.14)

Render's default Python runtime is 3.14. `langchain-pinecone` and its transitive dependency `pinecone-client` fail to install or import on 3.14 — the failure surfaces during `pip install` in the Build step, not at runtime. Pinning `PYTHON_VERSION=3.13` in Render env vars forces the correct runtime.

**Trade-off:** None — this is a compatibility constraint from upstream, not a design choice. Documented so future-me knows why the env var exists and doesn't casually remove it.

**Action:** Watch for `langchain-pinecone` and `pinecone-client` releases that add 3.14 support. Once both support 3.14, the pin can be removed. Do NOT pin patch version (`3.13.x`) — Render's minor-version pinning is enough and patch pins break builds when Render deprecates old patches.

---

### 3. Dual dependency management (`requirements.txt` + `pyproject.toml`)

Build Command runs both `pip install -r requirements.txt` and `pip install -e .`. The first installs third-party libraries; the second installs the local `rag_basics` package in editable mode so imports like `from rag_basics.langchain_query_pinecone import ...` resolve on Render's container.

**Trade-off:** Two dependency files is redundant in principle — everything in `requirements.txt` could live under `pyproject.toml`'s `dependencies` field. Kept both because `requirements.txt` gives explicit pinning for deploy reproducibility while `pyproject.toml` handles the local package layout. Collapsing to one file is a cleanup task, not a bug.

**Action:** If migrating to a single source of truth, move `requirements.txt` contents into `pyproject.toml` under `[project.dependencies]` and update Build Command to just `pip install -e .`. Deferred until there's a reason to touch dependency management.

---

### 4. `langchain_query_pinecone.py` executes I/O at module top level

`TextLoader` reads `knowledge_base.txt` and BM25 index construction both run at import time, not inside a function. Any code that imports this module pays the file-read cost and the BM25 build cost immediately, even in tests or scripts that don't query.

**Why it happened:** Fast path during Pinecone cutover. Refactoring to lazy init would have added a change to an already-large migration.

**Trade-off:** Correctness now, cleanup later. The behavior is right; the shape is wrong.

**Action:** Move to a lazy singleton pattern (build on first query, cache thereafter). Deferred.

---

### 5. BM25 uses Method A (rebuild from `knowledge_base.txt` at startup)

BM25 index is not pickled and cached — it's rebuilt from the source text file every time the service starts. This was chosen over Method C (pickle cache) because Pinecone vectors and BM25 both derive from `knowledge_base.txt`, so a single source of truth makes desync structurally impossible.

**Trade-off:** Startup cost vs. consistency risk. Method C is faster to boot but re-introduces a class of bugs where the pickle and Pinecone drift apart after an ingest. Method A is slower to boot but that class of bug can't exist.

**Action:** Monitor startup time as `knowledge_base.txt` grows. If cold start crosses ~10s from BM25 alone, revisit — but don't switch back to Method C without also solving the desync problem (e.g., version stamp on both).

---

### 6. Render free tier cold start (~30–60s)

After ~15 min idle, Render free tier spins the container down. First request wakes it up: container boot + Python startup + module-level I/O (Issue #4) + BM25 rebuild (Issue #5) all stack up. Second request onward is fast.

**Trade-off:** $0 hosting vs. UX. Fine for solo development, not fine for colleagues who will assume the service is broken on first click.

**Action before colleague testing:** Either (a) upgrade to Render paid tier for always-on, or (b) tell colleagues explicitly "first request takes up to a minute, wait for it." Option (a) is the professional answer; option (b) is the temporary answer.

---

### 7. No fail-fast check on required environment variables

`PINECONE_API_KEY`, `OPENAI_API_KEY`, and `COHERE_API_KEY` are read lazily by their client libraries — if any is missing, the service starts fine and only fails on the first actual query, with an error message that points at the API call, not at the missing config.

**Trade-off:** None, really. This is just tech debt.

**Action:** Add a startup check that verifies all three env vars are present and non-empty before FastAPI accepts traffic. Fail loudly at boot, not quietly at query time.

---

### 8. Knowledge base curation is manual and unversioned

`knowledge_base.txt` is edited by hand and committed to git. There's no schema, no validation, no diff-checking against the Pinecone index. If someone edits the file but forgets to re-run `langchain_ingest_pinecone.py`, Pinecone and BM25 will drift (BM25 rebuilds from the file at startup; Pinecone doesn't).

**Trade-off:** Simplicity vs. safety. Manual editing is fine when there's one editor (me); it becomes fragile once anyone else touches the KB.

**Action:** Before opening this to any second editor, add an ingest script that (a) diffs the file against a stored hash and (b) refuses to skip re-embedding when the hash changed.

---

*Note on deployment scope: current setup is single-region (Pinecone serverless in AWS us-east-1, Render in Oregon). This is deliberate for cost and simplicity, not an oversight — multi-region would only be justified after user base and latency SLOs demand it.*

## Redeployment Runbook

1. Push code to `main` branch
2. Both services auto-deploy in parallel
3. Wait for build + startup completion in Render dashboard
4. Verify FastAPI:
```bash
   curl -X POST https://ai-immigration-assistant.onrender.com/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "test", "session_id": "verify-1"}'
```
   Expected: HTTP 200 with `answer` and `sources` fields
5. Verify Streamlit: open URL, ask a question, check answer + sources render correctly

## History

- **2026-07-23 (Day 65)**: Migrated from ChromaDB (local `persist_directory`) to Pinecone (serverless), zero downtime. Diagnosed and resolved three deploy blockers during cutover: (a) editable install required in Build Command for local package imports, (b) Python version pinning to 3.13 (Render's 3.14 default breaks `langchain-pinecone`), (c) missing env vars for Pinecone and Cohere.
- **2026-07-27 (Day 66)**: Completed Known Issues section (8 items) with trade-offs and actions. Retired the Day 65 placeholder.