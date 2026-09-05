@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

:ask_target
set "TARGET="
set /p "TARGET=target (separate multiple values with spaces): "
if "%TARGET%"=="" (
    echo target ha hissu desu.
    goto ask_target
)

".venv\Scripts\python.exe" src\main.py --target %TARGET%

echo.
pause

endlocal
