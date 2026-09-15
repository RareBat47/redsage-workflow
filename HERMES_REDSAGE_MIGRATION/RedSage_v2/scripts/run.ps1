# RedSage v2 prod-like local launcher (Windows PowerShell)
# Serves the built frontend and the API from a single backend process.
# Run scripts/build.ps1 first if frontend/dist is missing.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path -LiteralPath (Join-Path $root 'frontend\dist\index.html'))) {
    Write-Error 'Frontend build not found. Run scripts\build.ps1 first.'
    exit 1
}

Write-Host 'RedSage v2 running at http://127.0.0.1:8000' -ForegroundColor Green
Push-Location $root
try {
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
}
finally {
    Pop-Location
}
