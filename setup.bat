@echo off
REM RUSS RAG Tutor - Quick Setup Script for Windows
REM Run this script to set up and start the RUSS application

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo RUSS: RAG-Based Tutor for Specific Subjects
echo ======================================================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.9+ is required but not found
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python !PYTHON_VERSION! found
echo.

REM Step 2: Install dependencies
echo [2/5] Installing Python dependencies...
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Step 3: Create data directories
echo [3/5] Creating data directories...
if not exist "data\chromadb" mkdir data\chromadb
if not exist "data\uploads" mkdir data\uploads
if not exist "data\curriculum" mkdir data\curriculum
echo ✓ Data directories created
echo.

REM Step 4: Validate imports
echo [4/5] Validating application setup...
python validate.py
echo.

REM Check validation result
if errorlevel 1 (
    echo ❌ Validation failed. Please check the errors above.
    pause
    exit /b 1
)

REM Step 5: Instructions
echo [5/5] Setup complete!
echo.
echo ======================================================================
echo ✓ RUSS is ready to run!
echo ======================================================================
echo.
echo Next steps:
echo.
echo 1. In a new terminal, start Ollama:
echo    > ollama serve
echo.
echo 2. In another terminal, pull the required models (first time only):
echo    > ollama pull llama3.2 nomic-embed-text llama-guard3:1b
echo.
echo 3. Then start the application:
echo    > streamlit run app.py
echo.
echo 4. Open http://localhost:8501 in your browser
echo.
echo ======================================================================
echo For help, see README.md
echo ======================================================================
echo.

pause
