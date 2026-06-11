# What you need to do — VenturePilot AI

Use this as a shared task list between **frontend (`main`)** and **agents/API (`agent-backend`)**.

---

## Branch roles

| Branch | Who | Contains |
|--------|-----|----------|
| **`main`** | Harshal (UI) | `frontend/` only — no Python backend in repo |
| **`agent-backend`** | You (agents + API) | Full stack: `agents/`, `backend/`, `rag/`, `shared/` |

Do **not** merge blindly: `main` README used to describe a local backend that does not exist on that branch.

---

## Your side (agents / backend / GCP)

### Must-do before demo

- [ ] **Work on `agent-backend`** — all agent and API changes happen here.
- [ ] **GCP / Gemini access**
  - Create or use a GCP project.
  - Either: Gemini API key (`GOOGLE_API_KEY`), **or** Vertex (`GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`).
- [ ] **Test live ADK once**
  ```bash
  # In .env on agent-backend:
  DEMO_MODE=false
  GOOGLE_API_KEY=...
  ```
  Run sample validation; confirm market/front_desk return real model output (not only static demo JSON).
- [ ] **Deploy backend to Cloud Run**
  ```bash
  gcloud run deploy venturepilot-backend \
    --source . \
    --dockerfile backend/Dockerfile \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DEMO_MODE=false,GOOGLE_API_KEY=YOUR_KEY,CORS_ORIGINS=https://YOUR-FRONTEND-URL"
  ```
  Copy the service URL (e.g. `https://venturepilot-backend-xxxxx.run.app`).
- [ ] **Share API URL with Harshal** so `main` frontend can set `NEXT_PUBLIC_API_URL`.
- [ ] **Smoke test deployed API**
  - `GET /health`
  - `POST /api/validation/start` + open SSE stream + `GET /api/reports/{id}`

### Should-do if time allows

- [ ] **Vertex AI Search** for market agent: `USE_MOCK_RETRIEVAL=false`, `VERTEX_SEARCH_DATA_STORE=...`
- [ ] **MongoDB Atlas** — set `MONGODB_URI` on Cloud Run (optional; in-memory works for demo)
- [ ] **Elastic MCP** for competitor agent (optional; mock is OK for hackathon)
- [ ] **2-minute demo script** — one sample idea, narrate agent timeline, show PDF

### Agent backlog (pick in order)

1. Harden **front_desk** reject/clarify paths  
2. **market_research** + real or clearly labeled mock citations  
3. **competitor_analysis** / **legal** beyond “framework” wording  
4. **scoring** stability (rubric + LLM)  
5. **debate** — only if you have time; not required for v1  

Details: **`AGENTS.md`**

### Git hygiene (one-time)

```bash
git rm --cached frontend/next-env.d.ts
git commit -m "Stop tracking auto-generated next-env.d.ts"
```

---

## Harshal’s side (frontend on `main`)

### Must-do

- [ ] Keep UI work on **`main`** (or PR into `main`).
- [ ] **Remove reliance on local backend** in docs — frontend calls **Cloud Run API** only.
- [ ] Set environment variable for production/preview:
  ```bash
  # frontend/.env.local
  NEXT_PUBLIC_API_URL=https://YOUR-CLOUD-RUN-URL
  ```
- [ ] Deploy frontend (Vercel / Cloud Run / Firebase Hosting).
- [ ] Confirm CORS: backend `CORS_ORIGINS` must include the deployed frontend origin.

### Optional (low priority for hack)

- [ ] Cap SSE log list length in `dashboard.tsx` if UI feels slow during agent run.
- [ ] Ignore perf while ML training runs locally — not blocking.

---

## Shared / either person

- [ ] Agree on **one demo startup idea** (sample text in UI is fine).
- [ ] Record a **short screen capture**: idea → agent timeline → report → PDF.
- [ ] Update GitHub repo description: link to live frontend + note API on `agent-backend` branch.
- [ ] After backend URL is stable: update **`main` README** (frontend-only section) — template below.

---

## Frontend-only README snippet (for `main` branch)

Put this on `main` so GitHub does not imply a local Python backend:

```markdown
## Run frontend

cd frontend && npm install && npm run dev

## API

This branch is UI only. Set:

NEXT_PUBLIC_API_URL=https://<your-cloud-run-backend>

Backend source: branch `agent-backend`.
```

---

## Quick reference — env vars (backend deploy)

| Variable | You set when |
|----------|----------------|
| `GOOGLE_API_KEY` | Using AI Studio / API key auth |
| `GOOGLE_GENAI_USE_VERTEXAI` | `true` for Vertex-backed Gemini |
| `GOOGLE_CLOUD_PROJECT` | Vertex or Vertex Search |
| `DEMO_MODE` | `false` for live ADK; `true` for safe fallback demo |
| `USE_MOCK_RETRIEVAL` | `true` until Search data store is ready |
| `CORS_ORIGINS` | Your deployed frontend URL |
| `MONGODB_URI` | Optional persistence |

---

## When stuck

| Problem | Check |
|---------|--------|
| Frontend 404 on API | `NEXT_PUBLIC_API_URL`, backend running, CORS |
| Always demo JSON | `DEMO_MODE=true` or ADK import failure — use Python **3.11** |
| ADK errors | `pip install -r backend/requirements.txt`, `import google.adk` |
| SSE stops early | Backend logs; session id; `/api/validation/{id}/stream` |

---

## Suggested this week

| Day | You | Harshal |
|-----|-----|---------|
| 1 | Live ADK test + Cloud Run deploy | Point frontend at API URL |
| 2 | Market RAG or better citations | UI polish / deploy frontend |
| 3 | Competitor or legal upgrade | Demo recording |
| 4 | Dry-run demo + fix failures | Same |

You do **not** need to finish Debate or perfect frontend perf for a strong hackathon story. **Visible multi-agent workflow + one live Gemini path + deployed URL** is enough.
