# Immigration Consulting RAG Assistant

A production RAG system answering Canadian immigration policy questions for consultants at Jianuo International, where I work part-time. Built and deployed solo.

**Live:** https://ai-immigration-assistant.onrender.com — on Render's free tier, so the first request takes 30–50s to wake the container.

---

## Problem

Immigration consultants answer the same policy questions repeatedly, from source material that changes without notice. Getting an answer wrong is worse than not answering: a consultant who relays a confidently stated but outdated eligibility rule to a client causes real harm.

That constraint shaped most of the design decisions below. **An honest "I don't have that information" is a better outcome than a fluent wrong answer.**

---

## Architecture

```
Query
  │
  ├─ Relevance gate ──── off-topic ──→ decline
  │
  ├─ Retrieval
  │    ├─ Dense (text-embedding-3-small → Pinecone, cosine)
  │    └─ BM25 (sparse keyword)
  │           └─ merged → top-6
  │
  ├─ Rerank (Cohere rerank-v3.5) → top-3
  │
  ├─ Generation (gpt-4o-mini, structured Pydantic output)
  │
  └─ URL guardrail (deterministic, outside the LLM)
```

**Stack:** Python · LangGraph · Pinecone · OpenAI · Cohere · FastAPI · Streamlit · Render

**Retrieval:** bi-encoder for fast coarse recall, cross-encoder rerank for precision on the shortlist. The bi-encoder is cheap enough to run over the full index; the cross-encoder is accurate enough to be worth ~100–300ms and an API call on six candidates.

**Indexing:** `MarkdownHeaderTextSplitter` on `##` headers, with a recursive character fallback for sections over 1200 characters. Category metadata is duplicated into `page_content` — metadata fields are not embedded, so anything that needs to be retrievable has to live in the text.

---

## Three things I got wrong, and what they taught me

### BM25 silently returned nothing on Chinese text

The knowledge base is Chinese. BM25's default tokenizer splits on whitespace, which produces almost no usable tokens for Chinese. The hybrid pipeline ran without error and returned results the whole time — the dense retriever was carrying it alone.

Ablation confirmed it: BM25-only scored 0.133 against a dense-only baseline of 0.533. **A component can fail completely without failing loudly.**

### The aggregate score was hiding a regression

I ran a stratified ablation across four configurations (15 queries × 4 configs). Dense-only and full hybrid+rerank both landed at 0.533 aggregate — no visible difference.

Broken down by category, reranking cost 20% cross-category precision (0.833 → 0.667) while gaining ~4.8% on multi-locality queries. The aggregate averaged the two into silence.

I kept reranking, since the failure mode it prevents matters more here than the one it introduces, but wrote down the scale conditions that should trigger revisiting the decision. See [`decisions.md`](decisions.md).

### The model answered from its own weights

On questions the knowledge base couldn't address, the model sometimes produced a correct-looking answer drawn from its training data rather than the retrieved context. Retrieval succeeded, output looked right, and no metric flagged it.

The fix wasn't a better prompt. Prompts are requests, and a non-deterministic system can decline a request. Safety boundaries belong in deterministic code outside the LLM — the URL guardrail holds by construction, not because the model was asked nicely.

---

## Evaluation

`evaluate.py` runs a stratified test set across four retrieval configurations and exports per-query, per-category results to CSV. Stratification is the point: as above, aggregate numbers hid the regression that mattered.

---

## Layout

| File | |
|---|---|
| `langchain_query_pinecone.py` | Retrieval + generation pipeline |
| `langchain_ingest_pinecone.py` | Chunking, metadata schema, indexing |
| `agent_basic.py` | LangGraph agent, 4 tools, checkpointed sessions |
| `agentic_rag.py` | Agentic retrieval loop |
| `evaluate.py` | Stratified ablation harness |
| `app.py` | FastAPI service |
| `streamlit_app.py` | Frontend |
| `decisions.md` | Architecture decision records |
| `anti-patterns.md` | Technical mistakes, logged as they happened |

## Running locally

```bash
pip install -e .                          # from repo root
python -m rag_basics.langchain_ingest_pinecone
python -m rag_basics.app
```

Requires `OPENAI_API_KEY`, `PINECONE_API_KEY`, `COHERE_API_KEY`.
