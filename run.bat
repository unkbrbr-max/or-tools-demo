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
set /p "TARGET=target: "
if "%TARGET%"=="" (
    echo target ha hissu desu.
    goto ask_target
)

set "LIMIT="
set /p "LIMIT=limit: "

set "ARGS=--target %TARGET%"
if not "%LIMIT%"=="" set "ARGS=%ARGS% --limit %LIMIT%"

".venv\Scripts\python.exe" src\main.py %ARGS%

echo.
pause

endlocal
