# VenturePilot AI — Frontend

**Partner track: MongoDB** | [Full stack on `agent-backend`](https://github.com/harshalDharpure/Devrepo/tree/agent-backend)

Startup intelligence dashboard (Next.js 15). This branch is **UI only** — connects to the **Cloud Run API** on `agent-backend`.

| Branch | Purpose |
|--------|---------|
| **`main`** (here) | Frontend |
| **`agent-backend`** | API + Google ADK agents + MongoDB Atlas |

**Submission guide:** [SUBMISSION.md](https://github.com/harshalDharpure/Devrepo/blob/agent-backend/SUBMISSION.md) · **Video script:** [VIDEO_SCRIPT.md](https://github.com/harshalDharpure/Devrepo/blob/agent-backend/VIDEO_SCRIPT.md)

---

## Quick start

```bash
cd frontend
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=https://your-cloud-run-backend-url
npm install && npm run dev
```

Open **http://localhost:3000**

---

## Deploy on Vercel

1. Import repo `harshalDharpure/Devrepo`
2. Branch: **`main`**
3. Root directory: **`frontend`**
4. Environment variable: `NEXT_PUBLIC_API_URL` = your Cloud Run backend URL
5. Update backend `CORS_ORIGINS` to your Vercel URL

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
