from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from backend.database import SessionLocal, init_db
from backend.routers import projects, scope, tasks, evidence, proposals, findings, reports, audit, assets, search, archives, mentor
from backend.services.static_frontend import frontend_dist_available, missing_frontend_html, mount_frontend
from backend.services.recovery_service import reconcile_storage_and_db

app=FastAPI(title="RedSage v2 Core Engine",version="2.0.0-mvp")
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:5173","http://localhost:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(projects.router); app.include_router(scope.router); app.include_router(tasks.router); app.include_router(evidence.router); app.include_router(proposals.router); app.include_router(findings.router); app.include_router(reports.router); app.include_router(audit.router); app.include_router(assets.router); app.include_router(search.router); app.include_router(archives.router); app.include_router(mentor.router)
@app.on_event("startup")
def startup():
    init_db()
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
