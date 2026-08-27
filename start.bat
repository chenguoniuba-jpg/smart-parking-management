@echo off
echo ====================================
echo Smart Parking System
echo ====================================

where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: uv is required. Install it from https://docs.astral.sh/uv/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
uv sync
if %errorlevel% neq 0 exit /b 1

echo [2/3] Initializing the demo database...
uv run python -m backend.init_data
if %errorlevel% neq 0 exit /b 1

echo [3/3] Starting http://127.0.0.1:8000 ...
echo The initializer prints a generated password when ADMIN_PASSWORD is not set.
uv run python -m backend.main
