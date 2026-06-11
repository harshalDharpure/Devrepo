# VenturePilot AI — Agent Development Guide

Branch: **`agent-backend`** (backend + agents + RAG). The **`main`** branch is frontend-only and talks to a deployed API.

---

## How orchestration works today

```
FastAPI (backend/main.py)
    └── ValidationWorkflow (backend/services/workflow.py)   ← you own the graph
            ├── FrontDeskAgent
            ├── MarketResearchAgent  + Vertex/mock RAG
            ├── CompetitorAnalysisAgent
            ├── LegalAgent
            ├── ScoringAgent
            └── ReportGeneratorAgent
```

Each domain agent extends **`DomainAgent`** (`agents/base.py`):

1. Build an **`AgentDescriptor`** (instruction + optional Pydantic `output_schema`).
2. Optionally call **`run_adk_json()`** → Google ADK `Agent` + `InMemoryRunner` (when `DEMO_MODE=false`).
3. Fall back to **`_demo_*`** helpers if ADK fails or demo mode is on.

**Important for judges:** ADK runs **per specialist agent**, not as a single ADK Workflow graph. The **workflow** (parallel market + competitor + legal, SSE events, storage) is custom Python — that is intentional and fine for the hackathon.

---

## Agent status

| Agent | File | ADK live calls | RAG / tools | Notes |
|-------|------|----------------|-------------|--------|
| Front Desk | `agents/front_desk.py` | Yes | — | Extraction + clarifications |
| Market Research | `agents/market_research.py` | Yes | `rag/vertex_search.py` | Richest agent; prioritize here |
| Competitor | `agents/competitor_analysis.py` | Yes | Mock/framework | Upgrade + Elastic MCP later |
| Legal | `agents/legal.py` | Yes | Mock/framework | Geography-aware rules |
| Scoring | `agents/scoring.py` | Yes | — | Feed prior agent JSON |
| Report | `agents/report_generator.py` | Yes | — | PDF via `backend/services/pdf.py` |
| Debate | — | **Not built** | — | Do not document as live |

---

## Implementation order (recommended)

### Phase 1 — Demo-safe (current)

- [x] Workflow + SSE events
- [x] ADK `LlmAgent` wrapper in `agents/base.py`
- [x] Demo fallbacks (`DEMO_MODE=true`)
- [ ] Deploy backend to Cloud Run (see `YOUR_CHECKLIST.md`)
- [ ] Point `main` frontend at Cloud Run URL

### Phase 2 — Live Gemini + one real RAG path

1. Set `DEMO_MODE=false` and `GOOGLE_API_KEY` (or Vertex: `GOOGLE_GENAI_USE_VERTEXAI=true`).
2. Run one validation; confirm logs show ADK runner, not only demo JSON.
3. Market agent: set `USE_MOCK_RETRIEVAL=false` + `VERTEX_SEARCH_DATA_STORE` when data store exists.

### Phase 3 — Stronger specialists

1. **Competitor** — wire Elastic MCP (or keep mock with labeled citations).
2. **Legal** — tighten geography → regulation mapping in prompt + schema.
3. **Scoring** — add deterministic weights on top of LLM (reduce score drift).

### Phase 4 — Optional (post-hack)

- **Debate agent** — only if market vs legal/competitor outputs can contradict.
- ADK 2.x **Workflow** graph for the parallel research fan-out (narrative upgrade, not required).

---

## Adding or changing an agent

1. Define output model in **`shared/schemas.py`**.
2. Create **`agents/your_agent.py`** with `DomainAgent` + `AgentDescriptor`.
3. Register in **`build_agents()`** in `backend/services/workflow.py`.
4. Add steps in **`ValidationWorkflow._run()`** (and SSE labels in `_run_framework_agent` if parallel).
5. Extend **`ReportGeneratorAgent`** if the report needs new sections.
6. Update frontend **`lib/types.ts`** only if the API shape changes.

---

## ADK vs LlamaIndex (quick map)

| LlamaIndex | This repo |
|------------|-----------|
| Workflow / AgentWorkflow | `ValidationWorkflow` |
| Agent with structured output | `DomainAgent` + `output_schema` |
| Retriever / query engine | `rag/vertex_search.py` |
| Tool calls | Not yet; add as ADK tools on `Agent(..., tools=[...])` |
| Observability | FastAPI logs + SSE timeline in UI |

---

## Local run (agents branch only)

```bash
git checkout agent-backend
cp .env.example .env
pip install -r backend/requirements.txt

# Windows
set PYTHONPATH=.
py -3.11 -m uvicorn backend.main:app --reload --port 8000

# Frontend (second terminal)
cd frontend && npm install && npm run dev
```

Health check: `GET http://localhost:8000/health` → `"demo_mode": true/false`.

---

## Files to read first

1. `backend/services/workflow.py` — orchestration
2. `agents/base.py` — ADK integration
3. `agents/market_research.py` — reference implementation
4. `shared/schemas.py` — contracts
5. `rag/vertex_search.py` — retrieval

See **`YOUR_CHECKLIST.md`** for who does what before the demo.
