# VenturePilot AI — Hackathon Submission Pack

**Partner track:** MongoDB  
**Stack:** Google ADK + Gemini 2.5 Pro + MongoDB Atlas + Cloud Run + Next.js

---

## URLs (fill in after deploy)

| Item | URL |
|------|-----|
| **Live app** | `https://YOUR-VERCEL-URL.vercel.app` |
| **GitHub** | https://github.com/harshalDharpure/Devrepo |
| **Backend API** | `https://venturepilot-backend-xxxxx.run.app` |
| **Demo video** | `https://youtube.com/...` or Loom link |

---

## Devpost description (copy-paste)

```
VenturePilot AI is a multi-agent startup validation system powered by Gemini and Google ADK.

Unlike chatbots, it plans and executes a validation workflow: idea extraction, market research, competitor analysis, legal screening, scoring, and report generation—with live agent orchestration visible to the user.

MongoDB Atlas stores validation sessions, agent state, and final reports so multi-step agents maintain context across the pipeline.

Stack: Google ADK, Gemini 2.5 Pro, FastAPI, MongoDB Atlas, Cloud Run, Next.js.
```

**Track:** MongoDB

---

## Deploy commands (run in order)

### 1. Install Google Cloud SDK (if missing)

Download: https://cloud.google.com/sdk/docs/install  
Then: `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`

### 2. Deploy backend (from repo root, `agent-backend` branch)

```powershell
cd C:\Users\HARSHAL\Downloads\devp
gcloud run deploy venturepilot-backend `
  --source . `
  --dockerfile backend/Dockerfile `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars "DEMO_MODE=true,CORS_ORIGINS=http://localhost:3000,MONGODB_URI=YOUR_ATLAS_URI"
```

### 3. Deploy frontend on Vercel

1. Push `main` branch to GitHub
2. https://vercel.com → Import `harshalDharpure/Devrepo`
3. Root directory: **`frontend`**
4. Environment variable: `NEXT_PUBLIC_API_URL` = your Cloud Run backend URL
5. Deploy

### 4. Fix CORS

```powershell
gcloud run services update venturepilot-backend `
  --region us-central1 `
  --update-env-vars "CORS_ORIGINS=https://YOUR-VERCEL-URL.vercel.app"
```

### 5. MongoDB Atlas

1. https://mongodb.com/atlas → free M0 cluster
2. Database user + password
3. Network Access → Allow `0.0.0.0/0`
4. Connect → Drivers → copy URI → replace password
5. Update Cloud Run: `MONGODB_URI=mongodb+srv://...`

Collections created on first validation: `sessions`, `reports`

---

## GitHub About section

- Description: `Multi-agent startup validation | MongoDB track | Google ADK + Gemini`
- License: Apache License 2.0

---

## Screenshots for Devpost

1. Dashboard with idea input
2. Agent timeline running (SSE)
3. Final report with scores
4. MongoDB Atlas showing `sessions` / `reports` collections
