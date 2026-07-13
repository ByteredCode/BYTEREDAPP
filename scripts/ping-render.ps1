# Script: ping-render.ps1
# Descripción: Ping a Render para evitar spin-down (free tier)
# Uso: Ejecutar cada 15 minutos via Windows Task Scheduler

$url = "https://byteredapp.onrender.com/health"
$logFile = "C:\Users\amona\Desktop\BYTEREDAPP\scripts\ping-log.txt"

try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "$timestamp - OK ($($response.StatusCode))"
    Add-Content -Path $logFile -Value $entry
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "$timestamp - ERROR: $($_.Exception.Message)"
    Add-Content -Path $logFile -Value $entry
}

# Mantener log con máximo 500 líneas
if ((Get-Content $logFile | Measure-Object -Line).Lines -gt 500) {
    Get-Content $logFile -Tail 250 | Set-Content $logFile
}
