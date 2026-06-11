# VenturePilot AI — Cloud Run backend deploy
# Prerequisites: gcloud CLI installed, authenticated, project set

param(
    [string]$ProjectId = "",
    [string]$MongoUri = "",
    [string]$CorsOrigins = "http://localhost:3000"
)

if ($ProjectId) { gcloud config set project $ProjectId }

$envVars = "DEMO_MODE=true,CORS_ORIGINS=$CorsOrigins"
if ($MongoUri) { $envVars += ",MONGODB_URI=$MongoUri" }

Write-Host "Deploying venturepilot-backend to Cloud Run..."
gcloud run deploy venturepilot-backend `
    --source . `
    --dockerfile backend/Dockerfile `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars $envVars

Write-Host "Done. Copy the service URL for NEXT_PUBLIC_API_URL and CORS_ORIGINS."
