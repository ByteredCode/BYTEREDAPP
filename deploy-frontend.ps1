# ============================================================
# BYTEREDAPP - Script de despliegue del frontend
# ============================================================
# Build del frontend React + subida a Hostinger via GitHub
#
#   .\deploy-frontend.ps1
# ============================================================

param(
    [switch]$SkipBuild,
    [switch]$SkipPush
)

$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }

Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  BYTEREDAPP - Despliegue Frontend" -ForegroundColor Yellow
Write-Host "============================================`n"

# 1. Build del frontend
if (-not $SkipBuild) {
    Write-Step "1/3 Build del frontend"
    Set-Location "$PSScriptRoot\client"
    pnpm install
    pnpm build
    Write-OK "Build completado: client/dist"
    Set-Location $PSScriptRoot
}

# 2. Commit y push
if (-not $SkipPush) {
    Write-Step "2/3 Subiendo a GitHub"
    git add .
    git status
    $commit = Read-Host "Mensaje de commit (Enter para 'Deploy frontend')"
    if ([string]::IsNullOrEmpty($commit)) { $commit = "Deploy frontend" }
    git commit -m $commit
    git push origin main
    Write-OK "Codigo subido a GitHub"
}

# 3. Verificar
Write-Step "3/3 Verificar despliegue"
Write-Host "  Hostinger auto-desplegara desde GitHub en ~2-5 minutos"
Write-Host "  URL: https://byteredapp.com"
Write-Host ""
