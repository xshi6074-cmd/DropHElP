@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo  Manual Database Initialization
echo ========================================
echo.

cd backend
echo Running: python scripts/init_db.py
python scripts/init_db.py
echo.

if errorlevel 1 (
    echo [ERROR] Failed to initialize database
    echo.
    echo Trying alternative method...
    echo.
    python -c "import sys; sys.path.insert(0, 'src'); from scripts.init_db import init_database; import asyncio; asyncio.run(init_database())"
)

cd ..
echo.
pause
