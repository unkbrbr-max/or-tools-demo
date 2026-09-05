@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Installing dependencies...
call ".venv\Scripts\activate.bat"
pip install -r requirements.txt

echo.
echo Setup complete. Run with:
echo   run.bat --target 10000000 --limit 1

endlocal
