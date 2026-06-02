from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from backend.config import settings
from backend.services.pdf import build_report_pdf
from backend.services.storage import build_store
from backend.services.workflow import ValidationWorkflow
from shared.schemas import ClarificationRequest, ValidationStartRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = await build_store()
    app.state.workflow = ValidationWorkflow(store)
    yield


app = FastAPI(title="VenturePilot AI Backend", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "mock_retrieval": settings.use_mock_retrieval,
        "vertex_ai": settings.google_genai_use_vertexai,
    }


@app.post("/api/validation/start")
async def start_validation(request: ValidationStartRequest):
    workflow: ValidationWorkflow = app.state.workflow
    session = await workflow.start(request)
    return {"session_id": session.session_id, "status": session.status}


@app.get("/api/validation/{session_id}/stream")
async def stream_validation(session_id: str):
    workflow: ValidationWorkflow = app.state.workflow
    if await workflow.status(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return StreamingResponse(workflow.stream(session_id), media_type="text/event-stream")


@app.get("/api/validation/{session_id}/status")
async def validation_status(session_id: str):
    workflow: ValidationWorkflow = app.state.workflow
    session = await workflow.status(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/api/validation/{session_id}/clarify")
async def clarify_validation(session_id: str, request: ClarificationRequest):
    workflow: ValidationWorkflow = app.state.workflow
    session = await workflow.clarify(session_id, request)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.session_id, "status": session.status}


@app.get("/api/reports/{session_id}")
async def get_report(session_id: str):
    workflow: ValidationWorkflow = app.state.workflow
    report = await workflow.report(session_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/api/reports/{session_id}/pdf")
async def get_report_pdf(session_id: str):
    workflow: ValidationWorkflow = app.state.workflow
    report = await workflow.report(session_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    content = build_report_pdf(report)
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="venturepilot-{session_id}.pdf"'},
    )

