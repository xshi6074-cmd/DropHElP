# Kuaibang Dev Environment Startup Script
# Run with: .\start-dev.ps1

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kuaibang Dev Environment Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Gray
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running or not installed" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Docker is running" -ForegroundColor Green

# Step 1: Start Docker containers
Write-Host ""
Write-Host "[1/4] Starting PostgreSQL and Redis..." -ForegroundColor Yellow
docker-compose up -d postgres redis 2>&1 | Out-Null
$composeResult = $LASTEXITCODE

if ($composeResult -ne 0) {
    Write-Host "[WARNING] Docker compose returned exit code $composeResult" -ForegroundColor Yellow
    Write-Host "  Checking if containers are already running..." -ForegroundColor Gray
}

# Check containers status
$pgRunning = docker ps -q -f name=kuaibang-db
$redisRunning = docker ps -q -f name=kuaibang-redis

if ($pgRunning -and $redisRunning) {
    Write-Host "[OK] Database containers are running" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to start containers" -ForegroundColor Red
    exit 1
}

# Step 2: Wait for database
Write-Host ""
Write-Host "[2/4] Waiting for database to be ready..." -ForegroundColor Yellow
$ready = $false
$attempts = 0
while (-not $ready -and $attempts -lt 30) {
    docker exec kuaibang-db pg_isready -U postgres > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
    } else {
        Write-Host "  Waiting for PostgreSQL... ($attempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $ready) {
    Write-Host "[ERROR] Database failed to start" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] PostgreSQL is ready" -ForegroundColor Green

# Step 3: Initialize database
Write-Host ""
Write-Host "[3/4] Initializing database tables..." -ForegroundColor Yellow

$originalLocation = Get-Location
Set-Location backend

$env:PYTHONPATH = "src"
try {
    $output = python scripts/init_db.py 2>&1
    Write-Host $output
    Write-Host "[OK] Database initialization completed" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Database init had issues" -ForegroundColor Yellow
    Write-Host "  Error: $_" -ForegroundColor Gray
}

Set-Location $originalLocation

# Step 4: Start backend
Write-Host ""
Write-Host "[4/4] Starting backend server..." -ForegroundColor Yellow

$backendPath = Join-Path $PSScriptRoot "backend"
$cmd = "cd /d `"$backendPath`" && set PYTHONPATH=src && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process cmd -ArgumentList "/k", $cmd -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "PostgreSQL: localhost:5432" -ForegroundColor Gray
Write-Host "Redis:      localhost:6379" -ForegroundColor Gray
Write-Host ""

# Keep window open
Read-Host "Press Enter to exit"
