@echo off
setlocal
cd /d "%~dp0"
title PadelVision AI v0.4

echo =============================================
echo        PADELVISION AI v0.4
echo   Technique Coach + Official Rules Agent
echo =============================================
echo.

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3.12 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.12"
    if not defined PYTHON_CMD py -3.11 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.11"
    if not defined PYTHON_CMD py -3.10 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3.10"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo Python was not found.
    echo Please install Python 3.10, 3.11, or 3.12 and run this file again.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating the local Python environment...
    %PYTHON_CMD% -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Installing or checking required packages...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Package installation failed.
    echo Make sure you are using Python 3.10, 3.11, or 3.12 and have internet access.
    pause
    exit /b 1
)

echo.
echo Starting PadelVision AI...
echo Your browser should open automatically.
echo Keep this window open while you use the application.
echo.

streamlit run app.py
pause
