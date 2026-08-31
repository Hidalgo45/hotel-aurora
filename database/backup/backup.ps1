# =============================================================================
#  Hotel Aurora - Respaldo de la base de datos (Windows / PowerShell)
#  Criterio 1.5 de la rubrica: estrategia basica de respaldo
#
#  Uso:
#      powershell -ExecutionPolicy Bypass -File database\backup\backup.ps1
#
#  Genera dos archivos en la carpeta 'respaldos':
#    aurora_AAAA-MM-DD.dump   respaldo completo, formato custom (comprimido)
#    esquema_AAAA-MM-DD.sql   solo la estructura, legible y versionable
# =============================================================================

$ErrorActionPreference = "Stop"

# ---- Configuracion: se lee del archivo .env del proyecto ----
$raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$envFile = Join-Path $raiz ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "No se encontro el archivo .env en $raiz" -ForegroundColor Red
    exit 1
}

$config = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*)$') { $config[$matches[1]] = $matches[2].Trim() }
}

$destino = Join-Path $raiz "respaldos"
New-Item -ItemType Directory -Force -Path $destino | Out-Null

$fecha = Get-Date -Format "yyyy-MM-dd"
$env:PGPASSWORD = $config["DB_PASSWORD"]

Write-Host ""
Write-Host "  Respaldando $($config['DB_NAME'])..." -ForegroundColor Cyan

# ---- 1. Respaldo completo en formato custom ----
# --format=custom permite restaurar tablas por separado y comprime al vuelo
pg_dump --host=$($config["DB_HOST"]) --port=$($config["DB_PORT"]) `
        --username=$($config["DB_USER"]) --dbname=$($config["DB_NAME"]) `
        --format=custom --compress=9 `
        --file="$destino\aurora_$fecha.dump"

# ---- 2. Solo el esquema, para versionarlo junto al codigo ----
pg_dump --host=$($config["DB_HOST"]) --port=$($config["DB_PORT"]) `
        --username=$($config["DB_USER"]) --dbname=$($config["DB_NAME"]) `
        --schema-only `
        --file="$destino\esquema_$fecha.sql"

$env:PGPASSWORD = $null

# ---- 3. Retencion: se conservan los ultimos 7 respaldos diarios ----
Get-ChildItem "$destino\aurora_*.dump" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 7 |
    Remove-Item -Force

Write-Host "  Listo. Archivos en: $destino" -ForegroundColor Green
Get-ChildItem "$destino" | Format-Table Name, @{N="Tamano (KB)";E={[math]::Round($_.Length/1KB,1)}}, LastWriteTime
Write-Host ""
Write-Host "  Recordatorio: un respaldo que nunca se restauro no cuenta como respaldo." -ForegroundColor Yellow
Write-Host "  Ver database\backup\restore.md para la prueba de restauracion." -ForegroundColor Yellow
Write-Host ""
