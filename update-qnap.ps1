# ============================================================
# BYTEREDAPP - Script de actualizacion en QNAP NAS
# ============================================================
# Ejecutar cuando se hagan cambios en el codigo del servidor
# Para actualizar SOLO el backend (sin recrear MySQL/Redis)
#
#   .\update-qnap.ps1
# ============================================================

param(
    [string]$QnapIp = "192.168.1.13",
    [string]$QnapUser = "admin",
    [string]$ProjectPath = "/share/CACHEDEV1_DATA/Docker/byteredapp",
    [string]$LocalPath = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "  [OK] $msg" -ForegroundColor Green }

Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  BYTEREDAPP - Actualizando backend" -ForegroundColor Yellow
Write-Host "============================================`n"

# 1. Subir archivos actualizados del servidor
Write-Step "1/4 Subiendo archivos actualizados"

scp -r "$LocalPath\server\Dockerfile" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\requirements.txt" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\run.py" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\start.sh" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\alembic.ini" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"

$serverFolders = @("app", "alembic", "scripts")
foreach ($folder in $serverFolders) {
    $localFolder = "$LocalPath\server\$folder"
    if (Test-Path $localFolder) {
        scp -r "$localFolder" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
        Write-OK "server/$folder"
    }
}

# 2. Rebuild imagen
Write-Step "2/4 Rebuildando imagen Docker"
ssh "${QnapUser}@${QnapIp}" "cd ${ProjectPath} && docker build -t byteredapp-server ./server"
Write-OK "Imagen reconstruida"

# 3. Reiniciar solo el server
Write-Step "3/4 Reiniciando contenedor server"
ssh "${QnapUser}@${QnapIp}" "cd ${ProjectPath} && docker compose up -d --force-recreate server"
Write-OK "Server reiniciado"

Start-Sleep -Seconds 10

# 4. Verificar
Write-Step "4/4 Verificando"
ssh "${QnapUser}@${QnapIp}" "docker ps --format 'table {{.Names}}\t{{.Status}}' --filter name=byteredapp"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  ACTUALIZACION COMPLETADA" -ForegroundColor Green
Write-Host "  Backend: https://api.byteredapp.com" -ForegroundColor Yellow
Write-Host "============================================`n"
