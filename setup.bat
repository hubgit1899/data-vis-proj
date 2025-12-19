@echo off
REM Setup script for Windows
REM Run with: setup.bat

echo ================================
echo   Traffic Safety Analysis Setup
echo ================================

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo X Python is not installed. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ================================
echo   Setup Complete!
echo ================================
echo.
echo To run the analysis:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run the analysis script:
echo      python analysis-code\analysis_report_v2.py
echo.
echo   3. Check the 'output\' folder for generated visualizations.
echo.
pause
