from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.services.static_frontend import (
    frontend_dist_available,
    missing_frontend_html,
    mount_frontend,
)


def test_missing_frontend_message_mentions_build_command():
    assert "npm run build" in missing_frontend_html()


def test_mount_frontend_serves_spa_and_preserves_api(tmp_path):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text("<div id='root'>Static UI</div>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('static');", encoding="utf-8")
    (dist / "vite.svg").write_text("<svg/>", encoding="utf-8")

    app = FastAPI()

    @app.get("/api/v1/health")
    def health():
        return {"status": "healthy"}

    assert mount_frontend(app, dist) is True
    client = TestClient(app)
    index = client.get("/")
    assert index.status_code == 200
    assert "Static UI" in index.text
    assert index.headers["content-type"].startswith("text/html")
    assert client.get("/assets/app.js").text == "console.log('static');"
    assert client.get("/vite.svg").text == "<svg/>"
    assert client.get("/api/v1/health").json() == {"status": "healthy"}
    assert client.get("/api/v1/missing").status_code == 404
    fallback = client.get("/some/spa/path")
    assert fallback.status_code == 200
    assert "Static UI" in fallback.text


def test_mount_frontend_false_when_dist_missing(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert mount_frontend(FastAPI(), empty) is False
    assert frontend_dist_available(empty) is False
