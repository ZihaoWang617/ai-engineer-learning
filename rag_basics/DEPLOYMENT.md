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

## Known Issues & Decisions


> ⚠️ **This section is incomplete.** Placeholder written on Day 65 (2026-07-23).
> Full explanations to be added on Day 66 after cognitive rest.
> The three issues to document:
> 1. Editable install required in Build Command
> 2. Python version pin required (Render defaults to 3.14, langchain-pinecone requires <3.14)
> 3. Dual dependency management (requirements.txt + pyproject.toml)

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

- **2026-07-23 (Day 65)**: Migrated from ChromaDB (local persist_directory) to Pinecone (serverless), zero downtime. Diagnosed and resolved editable install, Python version pinning, and env var propagation issues during cutover.