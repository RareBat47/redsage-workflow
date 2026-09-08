# RedSage v2 dev-mode launcher (Windows PowerShell)
# Starts the FastAPI backend and the Vite frontend dev server in separate windows.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

Write-Host 'Starting backend: http://127.0.0.1:8000' -ForegroundColor Green
Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $root

Write-Host 'Starting frontend dev server: http://127.0.0.1:5173' -ForegroundColor Green
Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory (Join-Path $root 'frontend')

Write-Host ''
Write-Host 'Dev mode ready.'
Write-Host '  Backend  http://127.0.0.1:8000'
Write-Host '  Frontend http://127.0.0.1:5173'
