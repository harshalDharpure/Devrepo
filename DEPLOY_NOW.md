# DEPLOY NOW — 30-minute checklist

## Already done
- [x] Code pushed: `main` + `agent-backend` on GitHub
- [x] LICENSE (Apache 2.0)
- [x] SUBMISSION.md + VIDEO_SCRIPT.md
- [x] MongoDB storage fix (Atlas used when `MONGODB_URI` is set)

---

## YOU must do these 4 things

### 1. Backend URL (pick ONE)

#### Option A — Render (no gcloud needed) ~10 min
1. Go to https://dashboard.render.com
2. **New → Blueprint**
3. Connect GitHub `harshalDharpure/Devrepo`, branch **`agent-backend`**
4. Render reads `render.yaml` automatically
5. Set env vars when prompted:
   - `CORS_ORIGINS` = your Vercel URL (update after step 2)
   - `MONGODB_URI` = your Atlas connection string (optional but recommended)
6. Copy service URL: `https://venturepilot-backend.onrender.com`

#### Option B — Google Cloud Run ~15 min
1. Install: https://cloud.google.com/sdk/docs/install
2. `gcloud auth login`
3. `gcloud config set project YOUR_PROJECT_ID`
4. Run:
```powershell
cd C:\Users\HARSHAL\Downloads\devp
git checkout agent-backend
.\scripts\deploy-backend.ps1 -CorsOrigins "https://YOUR-VERCEL-URL.vercel.app" -MongoUri "YOUR_ATLAS_URI"
```

---

### 2. Frontend on Vercel ~10 min
1. https://vercel.com → **Add New Project**
2. Import `harshalDharpure/Devrepo`
3. Branch: **`main`**
4. Root Directory: **`frontend`**
5. Environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-URL
   ```
6. Deploy → copy URL

---

### 3. Fix CORS
Update backend `CORS_ORIGINS` to your exact Vercel URL (no trailing slash).

Render: Dashboard → Service → Environment  
Cloud Run: `.\scripts\update-cors.ps1 -FrontendUrl "https://xxx.vercel.app"`

---

### 4. MongoDB Atlas ~5 min (for MongoDB track)
1. https://mongodb.com/atlas → free cluster
2. Database Access → user + password
3. Network Access → `0.0.0.0/0`
4. Connect → copy `mongodb+srv://...`
5. Add to backend env as `MONGODB_URI`
6. Run one validation → check Atlas → `venturepilot` db → `sessions`, `reports`

---

## Test before video
1. Open Vercel URL
2. Load sample idea → Validate
3. Wait for report
4. Download PDF

---

## Record video (3 min)
Follow **VIDEO_SCRIPT.md**

---

## Devpost
Copy description from **SUBMISSION.md** → Track: **MongoDB**

Fill in:
- Project URL = Vercel link
- GitHub = https://github.com/harshalDharpure/Devrepo
- Video = YouTube/Loom link

---

## Local dev (right now)
```powershell
# Terminal 1 - backend
git checkout agent-backend
$env:PYTHONPATH="."
py -3.11 -m uvicorn backend.main:app --port 8000

# Terminal 2 - frontend  
cd frontend
npm run dev
```
Open http://localhost:3000
