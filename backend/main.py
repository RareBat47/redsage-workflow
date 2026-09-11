from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import os
from backend.database import SessionLocal, ensure_db_ready
from backend.routers import projects, scope, tasks, task_steps, evidence, proposals, findings, reports, audit, assets, search, archives, mentor, workflow, workflow_digest
from backend.services.static_frontend import frontend_dist_available, missing_frontend_html, mount_frontend
from backend.services.recovery_service import reconcile_storage_and_db

# Defense in depth for the documented loopback-only posture. TestClient hosts
# are allowed so the suite keeps working; set REDSAGE_ALLOW_REMOTE=1 to opt out.
_LOOPBACK_CLIENTS = {"127.0.0.1", "::1", "localhost", "testclient", "testserver"}

app=FastAPI(title="RedSage v2 Core Engine",version="2.0.0-mvp")
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:5173","http://localhost:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.middleware("http")
async def enforce_loopback(request: Request, call_next):
    if os.getenv("REDSAGE_ALLOW_REMOTE", "").strip().lower() in {"1", "true", "yes"}:
        return await call_next(request)
    client_host = (request.client.host if request.client else "") or ""
    if client_host not in _LOOPBACK_CLIENTS:
        return JSONResponse({"detail": "Remote clients are not allowed in local mode"}, status_code=403)
    return await call_next(request)

app.include_router(projects.router); app.include_router(scope.router); app.include_router(tasks.router); app.include_router(task_steps.router); app.include_router(evidence.router); app.include_router(proposals.router); app.include_router(findings.router); app.include_router(reports.router); app.include_router(audit.router); app.include_router(assets.router); app.include_router(search.router); app.include_router(archives.router); app.include_router(mentor.router); app.include_router(workflow.router); app.include_router(workflow_digest.router)
@app.on_event("startup")
def startup():
    ensure_db_ready()
    db = SessionLocal()
    try:
        reconcile_storage_and_db(db)
    finally:
        db.close()

@app.get("/api/v1/health",tags=["System"])
def health():
    return {"status":"healthy","service":"RedSage v2 Engine","version":"2.0.0-mvp","human_in_the_loop":True}

if frontend_dist_available():
    mount_frontend(app)
else:
    @app.get("/", include_in_schema=False)
    def root_message():
        return HTMLResponse(missing_frontend_html())
