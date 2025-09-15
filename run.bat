@echo off
REM One-click script to run Assignment Calendar Sync on Windows

echo ======================================
echo 📚 ASSIGNMENT CALENDAR SYNC
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    echo    Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo First time setup detected!
    echo Let's configure your settings...
    echo.
    python setup.py
    
    if %errorlevel% neq 0 (
        echo Setup failed. Please try again.
        pause
        exit /b 1
    )
)

REM Check if dependencies are installed
python -c "import selenium" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install selenium requests python-dotenv pytz python-dateutil
)

REM Run the sync
echo.
echo Starting assignment sync...
echo ------------------------------
python python\simple_sync.py

echo.
echo Press any key to exit...
pause >nul