@echo off
echo ========================================
echo  Kuaibang Dev Environment Startup
echo ========================================
echo.

REM Check Docker
echo Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop first
    pause
    exit /b 1
)
echo [OK] Docker is running

echo.
echo [Step 1/4] Starting PostgreSQL and Redis...
docker-compose up -d postgres redis
if errorlevel 1 (
    echo [WARNING] Docker compose warning, checking containers...
)

docker ps | findstr kuaibang-db >nul
if errorlevel 1 (
    echo [ERROR] PostgreSQL container not running
    pause
    exit /b 1
)
docker ps | findstr kuaibang-redis >nul
if errorlevel 1 (
    echo [ERROR] Redis container not running
    pause
    exit /b 1
)
echo [OK] Database containers started

echo.
echo [Step 2/4] Waiting for database to be ready...
:check_db
docker exec kuaibang-db pg_isready -U postgres >nul 2>&1
if errorlevel 1 (
    echo   Waiting for PostgreSQL...
    timeout /t 2 /nobreak >nul
    goto check_db
)
echo [OK] PostgreSQL is ready

echo.
echo [Step 3/4] Initializing database tables...
cd backend
set PYTHONPATH=src
python scripts/init_db.py
echo.
cd ..

echo.
echo [Step 4/4] Starting backend server...
cd backend
start cmd /k "set PYTHONPATH=src && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

echo.
echo ========================================
echo  Services Started!
echo ========================================
echo.
echo API Docs: http://localhost:8000/docs
echo Health:   http://localhost:8000/health
echo.
echo PostgreSQL: localhost:5432
echo Redis:      localhost:6379
echo.
pause
