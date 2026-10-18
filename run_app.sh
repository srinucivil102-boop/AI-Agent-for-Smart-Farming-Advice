#!/bin/bash
# Setup and run script for Linux/Mac
echo "============================================================"
echo " AI Agent for Smart Farming Advice - Setup Script"
echo " IBM Granite + IBM Cloud + Multi-Agent System"
echo "============================================================"

echo ""
echo "[1] Checking Python..."
python3 --version || { echo "Python3 not found! Install from python.org"; exit 1; }

echo ""
echo "[2] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[3] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[4] Running tests..."
python test_agents.py

echo ""
echo "[5] Launching app..."
echo "    Open http://localhost:8501 in your browser"
streamlit run app.py
