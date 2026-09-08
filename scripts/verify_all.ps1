$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    $env:DATABASE_URL = "sqlite:///$($root.Replace('\', '/'))/data/verify_all.db"
    $env:CO_API_KEY = ''
    $env:COHERE_API_KEY = ''
    python -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"
    node --version
    python -m compileall -q backend
    pytest -m 'not e2e' -q
    Push-Location frontend
    try { npm ci; npm run build } finally { Pop-Location }
    python -m playwright install chromium
    $server = Start-Process python -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000' -PassThru -WindowStyle Hidden
    try {
        $ready = $false
        1..60 | ForEach-Object {
            if (-not $ready) {
                try { Invoke-WebRequest 'http://127.0.0.1:8000/api/v1/health' -UseBasicParsing | Out-Null; $ready = $true } catch { Start-Sleep -Milliseconds 500 }
            }
        }
        if (-not $ready) { throw 'RedSage server did not become ready' }
        pytest -m e2e -q
    } finally { Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue }
    python -c "from backend.database import SessionLocal; from backend.services.recovery_service import reconcile_storage_and_db; print(reconcile_storage_and_db(SessionLocal()))"
} finally { Pop-Location }
