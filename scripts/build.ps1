# RedSage v2 frontend production build (Windows PowerShell)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $root 'frontend')
try {
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
Write-Host 'Frontend build written to frontend/dist' -ForegroundColor Green
