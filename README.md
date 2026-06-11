# VenturePilot AI

**Partner track: MongoDB** | Stack: Google ADK + Gemini 2.5 Pro + MongoDB Atlas + Cloud Run

**Workflow-driven multi-agent startup validation system** powered by Google ADK + Gemini 2.5 Pro.

VenturePilot AI validates startup ideas using real-world evidence, RAG retrieval, legal risk screening, competitor analysis frameworking, and structured scoring — all coordinated by a visible backend workflow.

> **Branches:** UI on [`main`](https://github.com/harshalDharpure/Devrepo/tree/main) (frontend only → Cloud API). **This branch** (`agent-backend`) = FastAPI + agents + RAG.  
> **Your tasks:** [YOUR_CHECKLIST.md](./YOUR_CHECKLIST.md) · **Agent dev guide:** [AGENTS.md](./AGENTS.md)

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────────┐
│  Frontend   │────▶│              FastAPI Backend                      │
│  Next.js 15 │ SSE │  ValidationWorkflow → storage (Mongo / memory)    │
└─────────────┘     └──────────────────┬───────────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────────┐
                    │         Validation Workflow + ADK Agents           │
                    │  Front Desk → Market ∥ Competitor ∥ Legal → Score  │
                    └──────────────────┬───────────────────────────────┘
                                       │
        Vertex AI Search        Google ADK              Gemini 2.5 Pro
```

## Agent Pipeline

| Agent | Responsibility |
|-------|---------------|
| **Front Desk** | Validates idea quality, extracts context, clarifications |
| **Market Research** | TAM/SAM/SOM, trends — Vertex Search / mock RAG |
| **Competitor Analysis** | Framework + SWOT (Elastic later) |
| **Legal** | Compliance framework by geography |
| **Scoring** | 5-dimension scores |
| **Report** | Executive summary, lean canvas, PDF |

**Debate agent:** not implemented (by design for v1).

## MongoDB Integration

- Validation sessions and agent state stored in **MongoDB Atlas**
- Reports persisted for retrieval and PDF export
- Multi-agent workflow reads/writes cross-step state via MongoDB (`sessions`, `reports` collections)

---

## Quick Start (this branch)

```bash
cp .env.example .env
pip install -r backend/requirements.txt
set PYTHONPATH=.
py -3.11 -m uvicorn backend.main:app --reload --port 8000

cd frontend && cp .env.example .env.local && npm install && npm run dev
```

Open **http://localhost:3000** · Health: **http://localhost:8000/health**

Full details: **[AGENTS.md](./AGENTS.md)** · Owner checklist: **[YOUR_CHECKLIST.md](./YOUR_CHECKLIST.md)**

---

## Deploy

1. Deploy backend (this branch) to Cloud Run.  
2. Share URL with frontend on `main` → `NEXT_PUBLIC_API_URL`.  
3. Set `CORS_ORIGINS` on backend to the frontend origin.

---

## License

Apache 2.0 — Hackathon project.
