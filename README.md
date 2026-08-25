# Zihao Wang

AI Engineer focused on production LLM systems — RAG, agent orchestration, evaluation.

📍 Based in Vancouver, BC · targeting Toronto / GTA, open to Vancouver  
📧 wang.zihao10@northeastern.edu  
🔗 [LinkedIn](https://www.linkedin.com/in/zihaowang617/)

MS Computer Science @ Northeastern University Vancouver (April 2027). Currently building a production RAG assistant for immigration consultants at Jianuo International. Seeking AI Engineer Co-op for Winter/Spring 2027.

---

## Featured Projects

### 🇨🇦 Jianuo AI Immigration Assistant — Production RAG System

Production RAG system deployed for immigration consultants at Jianuo International. Handles Chinese-language queries over a knowledge base of Canadian immigration policies and authoritative IRCC sources.

**Stack:** LangChain 1.0 · LangGraph · Pinecone · OpenAI embeddings · Cohere rerank-v3.5 · BM25 · FastAPI · Streamlit · Render

**Key technical decisions:**
- **Deterministic URL resolution outside the LLM.** Agent returns `cited_link_ids`; code resolves URLs from the KB. Zero hallucinated citations, regardless of LLM output.
- **5-branch prompt decision rule** for scope control — separates chit-chat, dynamic-data queries, exact/partial KB matches, and KB gaps. Prevents over-generalization and surfaces knowledge boundaries.
- **Semantic header-based chunking** on policy documents; unified metadata schema across content chunks and authoritative external links (82 vectors, 19 L2 category groups).
- **Ablation study (4 configs × 15 queries):** BM25's default whitespace tokenizer silently fails on Chinese queries — contributes zero to retrieval. Cohere rerank shows high per-query variance (±0.333) with no aggregate gain at current KB scale. Findings drove architecture decisions logged in `decisions.md`.

**Links:** [Live Demo](https://ai-immigration-assistant-ui.onrender.com) · [API](https://ai-immigration-assistant.onrender.com) · [Code](./rag_basics) · [Architecture Decisions](./rag_basics/decisions.md)

---

### 👁️ InterAIct — Edge AI Emotion Detection for Autistic Children

🏆 **2nd Place**, Qualcomm × Microsoft × Northeastern EdgeAI Hackathon · March 2025 · 48-hour build

Real-time emotion detection + eye-attention tracking on Snapdragon edge device, designed to support engagement analysis for autistic children.

**My contributions:**
- **Fine-tuned ResNet18** for 6-class emotion classification (Natural, Anger, Fear, Joy, Sadness, Surprise) — 78% accuracy
- **Designed CombinedModel architecture** unifying emotion detection and eye-state detection into a single forward pass, deployable as one model
- **PyTorch → ONNX conversion pipeline** for Snapdragon edge deployment; chose `torch.jit.script` over trace due to branching logic in forward pass
- **Integrated open-source eye blink detection** as complementary attention signal

**Stack:** PyTorch · ResNet18 · ONNX · Snapdragon AI Hub · OpenCV

*Team hackathon project. Repo hosted on teammate's account.*

---

### 🎲 Kill Doctor Lucky — Full-Stack Java Board Game

CS5010 Programming Design Paradigm, Northeastern University · Fall 2025 · Grade: 94/95

Multi-player turn-based board game (based on the physical board game) with Java Swing GUI. Full MVC + dual-mode support.

**Technical highlights:**
- **Strict MVC architecture** — Model implements `ReadOnlyGameModel` interface; immutable `GameState` snapshots passed to View
- **Command design pattern** — every user action (Move, Attack, PickUp, MovePet) encapsulated as a Command object
- **Dual mode support** — same Model works with both `GraphicalController` (Swing GUI) and `TextController` (CLI), demonstrating clean layer separation
- **AI players via DFS** — computer opponents evaluate move trees and auto-attempt murder when conditions are favorable
- **85%+ test coverage** with JUnit 4; Controllers tested in isolation using mocked Model and View
- **Design patterns:** MVC · Command · Strategy · Facade · Observer

**Stack:** Java 11 · Swing · JUnit 4

**Links:** [Code](https://github.com/ZihaoWang617/CS5010_KillDoctorLucky) · [UML & Design Doc](https://github.com/ZihaoWang617/CS5010_KillDoctorLucky/blob/main/res/UML-Milestone4.pdf)

---

## Other Projects

- **AI Code Reviewer** — REST API with dual LLM support (OpenAI + Anthropic), function-calling dispatch pattern for automatic file reading across differing tool schemas. FastAPI + Pydantic + UUID-keyed JSON persistence. [Code](./code-reviewer) · [Live API](https://ai-engineer-learning.onrender.com)
- **Climate Resilience ML** — Regression pipeline optimizing fertilization from weather + soil data. Pandas + Scikit-learn. 🏆 2nd Place, Northeastern Climate Resilience Hackathon (Dec 2024).

---

## Repository Structure

This mono-repo tracks my AI engineering work. Highlighted project directories:

```
├── rag_basics/         Jianuo AI Immigration Assistant (production RAG)
├── code-reviewer/      AI Code Reviewer REST API
├── leetcode-notes/     NeetCode 150 progress
└── decisions.md        Architecture decision records
```

Each active project directory contains its own README with setup, architecture, and technical notes.
---

## About

MS Computer Science @ Northeastern University Vancouver · BS Applied Mathematics @ UC Davis · Immigration Consulting Associate @ Jianuo International (Sep 2025–present).

Focus areas: production LLM systems, RAG evaluation, agent orchestration, applied ML.