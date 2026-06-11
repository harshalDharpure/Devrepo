param([string]$FrontendUrl = "https://YOUR-VERCEL-URL.vercel.app")

gcloud run services update venturepilot-backend `
    --region us-central1 `
    --update-env-vars "CORS_ORIGINS=$FrontendUrl"
