# ============================================================
# BYTEREDAPP - Script de despliegue en QNAP NAS
# ============================================================
# Ejecutar desde PowerShell en el PC:
#   .\deploy-qnap.ps1
#
# Requisitos:
#   - SSH habilitado en el QNAP
#   - Docker instalado en el QNAP
#   - Archivo .env.qnap configurado (copiar de .env.qnap.example)
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
function Write-Err  { param([string]$msg) Write-Host "  [ERROR] $msg" -ForegroundColor Red }

Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  BYTEREDAPP - Despliegue en QNAP NAS" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  QNAP: ${QnapUser}@${QnapIp}"
Write-Host "  Destino: ${ProjectPath}"
Write-Host "============================================`n"

# ------------------------------------------------------------
# 1. Verificar prerequisitos
# ------------------------------------------------------------
Write-Step "1/7 Verificando prerequisitos"

# Verificar SSH
try {
    $sshTest = ssh -o ConnectTimeout=5 -o BatchMode=yes "${QnapUser}@${QnapIp}" "echo ok" 2>$null
    if ($sshTest -eq "ok") {
        Write-OK "Conexion SSH OK"
    } else {
        Write-Err "No se puede conectar por SSH a ${QnapIp}"
        exit 1
    }
} catch {
    Write-Err "SSH no disponible. Verifica que SSH este habilitado en el QNAP."
    exit 1
}

# Verificar Docker en QNAP
try {
    $dockerVersion = ssh "${QnapUser}@${QnapIp}" "docker --version" 2>$null
    Write-OK "Docker: $dockerVersion"
} catch {
    Write-Err "Docker no instalado en el QNAP"
    exit 1
}

# Verificar archivo .env.qnap
if (-not (Test-Path "$LocalPath\.env.qnap")) {
    Write-Err "Archivo .env.qnap no encontrado en $LocalPath"
    Write-Host "  Copia .env.qnap.example a .env.qnap y rellena los valores"
    exit 1
}
Write-OK "Archivo .env.qnap encontrado"

# Verificar docker-compose.qnap.yml
if (-not (Test-Path "$LocalPath\docker-compose.qnap.yml")) {
    Write-Err "Archivo docker-compose.qnap.yml no encontrado"
    exit 1
}
Write-OK "Archivo docker-compose.qnap.yml encontrado"

# ------------------------------------------------------------
# 2. Crear estructura de directorios en QNAP
# ------------------------------------------------------------
Write-Step "2/7 Creando directorios en QNAP"

ssh "${QnapUser}@${QnapIp}" @"
mkdir -p ${ProjectPath}/server
mkdir -p ${ProjectPath}/config
mkdir -p ${ProjectPath}/mysql-data
echo 'Directorios creados'
"@
Write-OK "Estructura de directorios creada"

# ------------------------------------------------------------
# 3. Subir archivos al QNAP
# ------------------------------------------------------------
Write-Step "3/7 Subiendo archivos al QNAP"

# docker-compose.yml
Write-Host "  Subiendo docker-compose.qnap.yml..."
scp "$LocalPath\docker-compose.qnap.yml" "${QnapUser}@${QnapIp}:${ProjectPath}/docker-compose.yml"
Write-OK "docker-compose.yml"

# .env
Write-Host "  Subiendo .env..."
scp "$LocalPath\.env.qnap" "${QnapUser}@${QnapIp}:${ProjectPath}/.env"
Write-OK ".env"

# Archivos del servidor
Write-Host "  Subiendo archivos del servidor..."
scp -r "$LocalPath\server\Dockerfile" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\requirements.txt" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\run.py" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\start.sh" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
scp -r "$LocalPath\server\alembic.ini" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
Write-OK "Archivos basicos del servidor"

# Copiar carpetas del servidor
$serverFolders = @("app", "alembic", "scripts")
foreach ($folder in $serverFolders) {
    $localFolder = "$LocalPath\server\$folder"
    if (Test-Path $localFolder) {
        Write-Host "  Subiendo server/$folder..."
        scp -r "$localFolder" "${QnapUser}@${QnapIp}:${ProjectPath}/server/"
        Write-OK "server/$folder"
    }
}

# Config del tunnel
Write-Host "  Subiendo config/cloudflared.yml..."
ssh "${QnapUser}@${QnapIp}" "mkdir -p ${ProjectPath}/config"
scp "$LocalPath\config\cloudflared.yml" "${QnapUser}@${QnapIp}:${ProjectPath}/config/"
Write-OK "config/cloudflared.yml"

# ------------------------------------------------------------
# 4. Build de la imagen Docker
# ------------------------------------------------------------
Write-Step "4/7 Construyendo imagen Docker (byteredapp-server)"

ssh "${QnapUser}@${QnapIp}" @"
cd ${ProjectPath}
docker build -t byteredapp-server ./server
"@
Write-OK "Imagen byteredapp-server construida"

# ------------------------------------------------------------
# 5. Parar contenedores existentes
# ------------------------------------------------------------
Write-Step "5/7 Parando contenedores existentes"

ssh "${QnapUser}@${QnapIp}" @"
cd ${ProjectPath}
docker compose down 2>/dev/null || true
"@
Write-OK "Contenedores parados"

# ------------------------------------------------------------
# 6. Levantar servicios
# ------------------------------------------------------------
Write-Step "6/7 Levantando servicios"

ssh "${QnapUser}@${QnapIp}" @"
cd ${ProjectPath}
docker compose up -d
"@
Write-OK "Servicios levantados"

# Esperar a que MySQL este listo
Write-Host "  Esperando a que MySQL este listo..."
Start-Sleep -Seconds 15

# ------------------------------------------------------------
# 7. Ejecutar migraciones y seed
# ------------------------------------------------------------
Write-Step "7/7 Ejecutando migraciones y seed"

ssh "${QnapUser}@${QnapIp}" @"
cd ${ProjectPath}
docker exec byteredapp-server alembic upgrade head
docker exec byteredapp-server python scripts/auto_seed.py || true
"@
Write-OK "Migraciones y seed completados"

# ------------------------------------------------------------
# Verificacion final
# ------------------------------------------------------------
Write-Host "`n============================================" -ForegroundColor Yellow
Write-Host "  DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Yellow

Write-Host "`nVerificando contenedores..."
ssh "${QnapUser}@${QnapIp}" "docker ps --format 'table {{.Names}}\t{{.Status}}'"

Write-Host "`nEndpoints:"
Write-Host "  Frontend:  https://byteredapp.com"
Write-Host "  Backend:   https://api.byteredapp.com"
Write-Host "  Health:    https://api.byteredapp.com/health"
Write-Host ""
