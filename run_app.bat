@echo off
echo ============================================================
echo  AI Agent for Smart Farming Advice - Setup Script
echo  IBM Granite + IBM Cloud + Multi-Agent System
echo ============================================================
echo.

echo [1] Checking Python installation...
python --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo Python found!

echo.
echo [2] Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Package installation failed!
    pause
    exit /b 1
)

echo.
echo [3] Running system tests...
python test_agents.py

echo.
echo [4] Launching Streamlit Application...
echo    Open http://localhost:8501 in your browser
echo.
streamlit run app.py

pause
