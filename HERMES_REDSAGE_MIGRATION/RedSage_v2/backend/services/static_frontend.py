"""Optional prod-like static serving of the built React frontend from FastAPI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
INDEX_FILE = DIST_DIR / "index.html"


def frontend_dist_available(dist_dir: Path = DIST_DIR) -> bool:
    return (dist_dir / "index.html").is_file()


def missing_frontend_html() -> str:
    return (
        "<!DOCTYPE html><html><head><title>RedSage v2</title></head>"
        "<body style='font-family:sans-serif;background:#101415;color:#dce7e3;"
        "padding:48px;line-height:1.7'>"
        "<h1>RedSage v2</h1>"
        "<p>The built frontend was not found.</p>"
        "<p>Run the following to build it, then reload this page:</p>"
        "<pre style='background:#1d2929;padding:16px;border-radius:6px'>"
        "cd frontend&#10;npm run build</pre>"
        "</body></html>"
    )


def mount_frontend(app: FastAPI, dist_dir: Path = DIST_DIR) -> bool:
    if not frontend_dist_available(dist_dir):
        return False
    assets_dir = dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    root = dist_dir.resolve()

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        if full_path:
            candidate = (root / full_path).resolve()
            if (
                candidate != root
                and root in candidate.parents
                and candidate.is_file()
                and candidate.suffix
            ):
                return FileResponse(str(candidate))
        return FileResponse(str(root / "index.html"))

    return True
