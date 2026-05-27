# VenturePilot AI

**Autonomous multi-agent startup validation system** powered by Google ADK + Gemini 2.5 Pro.

VenturePilot AI validates startup ideas using real-world evidence, RAG retrieval, web intelligence, legal analysis, competitor analysis, and structured scoring — all orchestrated through a visible multi-agent pipeline.

![Architecture](https://img.shields.io/badge/Google_ADK-Orchestration-4285F4) ![Gemini](https://img.shields.io/badge/Gemini-2.5_Pro-8E75B2) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688) ![Next.js](https://img.shields.io/badge/Next.js_15-Frontend-000)

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────────┐
│  Frontend   │────▶│              FastAPI Backend                      │
│  Next.js 15 │ SSE │  Orchestration Runner → MongoDB Atlas             │
└─────────────┘     └──────────────────┬───────────────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────────────┐
                    │           Google ADK Orchestrator                   │
                    │  ┌──────────┐  ┌─────────┐  ┌─────────┐         │
                    │  │Front Desk│→ │ Market  │  │Competitor│         │
                    │  └──────────┘  │ Research│  │ Analysis │         │
                    │                └────┬────┘  └────┬─────┘         │
                    │  ┌─────────┐  ┌────┴────┐  ┌────┴─────┐         │
                    │  │  Legal  │  │  Debate  │→│ Scoring  │→ Report │
                    │  └─────────┘  └─────────┘  └──────────┘         │
                    └──────────────────┬───────────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
        Vertex AI Search        Elastic MCP              Gemini 2.5 Pro
        (Market RAG)           (Competitor Intel)        (Structured Output)
```

## Agent Pipeline

| Agent | Responsibility |
|-------|---------------|
| **Front Desk** | Validates idea quality, extracts context, asks clarifying questions |
| **Orchestrator** | Dynamic agent invocation, state management, retries |
| **Market Research** | TAM/SAM/SOM, trends, growth opportunities via RAG |
| **Competitor Analysis** | Direct competitors, saturation, SWOT matrix |
| **Legal** | Compliance risks, regulations by geography |
| **Debate** | Contradiction detection, conflict resolution, confidence |
| **Scoring Engine** | 5-dimension validation scoring |
| **Report Generator** | Executive summary, lean canvas, PDF export |

## Quick Start

### Prerequisites

- **Python 3.11+** (required for Google ADK)
- Node.js 20+
- MongoDB (optional — falls back to in-memory)

### 1. Clone & Configure

```bash
cp .env.example .env
# Set GOOGLE_API_KEY for live Gemini calls, or keep DEMO_MODE=true
```

### 2. Backend

```bash
pip install -r backend/requirements.txt
# Windows
set PYTHONPATH=.
py -3.11 -m uvicorn backend.main:app --reload --port 8000

# macOS/Linux
export PYTHONPATH=.
python3.11 -m uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

### Docker (All Services)

```bash
docker-compose up --build
```

## Demo Walkthrough

1. Open the dashboard at `http://localhost:3000`
2. Click **"Load sample idea"** or paste your startup description
3. Click **"Validate Idea"**
4. Watch the live agent timeline:
   - *"Front Desk Agent validating idea…"*
   - *"Market Agent researching TAM/SAM/SOM…"*
   - *"Competitor Agent analyzing landscape…"*
   - *"Legal Agent checking regulations…"*
   - *"Debate Agent resolving conflicts…"*
5. View the structured report with scores, SWOT, lean canvas
6. Click **"Download PDF"** for the full report

### Sample Idea

> VenturePilot AI — an autonomous multi-agent platform that validates startup ideas using real-world evidence, RAG retrieval, competitor analysis, and legal compliance checks. Target audience is pre-seed founders and angel investors. B2B SaaS model with tiered pricing ($49-$499/mo). Focus on US and EU markets.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/validation/start` | Start validation pipeline |
| `GET` | `/api/validation/{id}/stream` | SSE agent event stream |
| `GET` | `/api/validation/{id}/status` | Session status |
| `POST` | `/api/validation/{id}/clarify` | Submit clarifications |
| `GET` | `/api/reports/{id}` | Get validation report JSON |
| `GET` | `/api/reports/{id}/pdf` | Download PDF report |
| `GET` | `/health` | Health check |

## Project Structure

```
venturepilot/
├── frontend/          # Next.js 15 + Tailwind + shadcn/ui
├── backend/           # FastAPI + SSE streaming + MongoDB
├── agents/            # Google ADK agent implementations
│   ├── front_desk.py
│   ├── orchestrator.py
│   ├── market_research.py
│   ├── competitor_analysis.py
│   ├── legal.py
│   ├── debate.py
│   ├── scoring.py
│   └── report_generator.py
├── rag/               # Vertex AI Search + Elastic retrieval
├── tools/             # LLM client + Elastic MCP
├── shared/            # Pydantic schemas
├── docker-compose.yml
└── cloudbuild.yaml
```

## Google Cloud Run Deployment

```bash
# Backend
gcloud run deploy venturepilot-backend \
  --source . \
  --dockerfile backend/Dockerfile \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=xxx,MONGODB_URI=xxx,DEMO_MODE=false

# Frontend
gcloud run deploy venturepilot-frontend \
  --source . \
  --dockerfile frontend/Dockerfile \
  --region us-central1 \
  --set-env-vars NEXT_PUBLIC_API_URL=https://venturepilot-backend-xxx.run.app
```

Or use Cloud Build:

```bash
gcloud builds submit --config cloudbuild.yaml
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | — | Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-pro` | LLM model |
| `DEMO_MODE` | `true` | Use mock LLM responses |
| `USE_MOCK_RETRIEVAL` | `true` | Use mock RAG data |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection |
| `ELASTIC_MCP_URL` | — | Elastic MCP server URL |
| `VERTEX_SEARCH_DATA_STORE` | — | Vertex AI Search data store |

## Tech Stack

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion
- **Backend:** FastAPI, asyncio, SSE streaming
- **AI:** Google ADK, Gemini 2.5 Pro, Pydantic structured output
- **Retrieval:** Vertex AI Search, Elastic MCP
- **Database:** MongoDB Atlas
- **Reports:** ReportLab PDF generation
- **Deploy:** Google Cloud Run, Docker

## License

Apache 2.0 — Built for hackathon demo purposes.
