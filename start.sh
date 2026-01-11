#!/bin/bash

echo "=========================================="
echo "Online Campus Weekly Sync - Setup & Run"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "onlinecampus" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv onlinecampus
    echo "✅ Virtual environment created"
else
    echo "[1/3] Virtual environment already exists"
fi

echo ""
echo "[2/3] Installing/Updating dependencies..."
onlinecampus/bin/pip install -q --upgrade pip
onlinecampus/bin/pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "[3/3] Running weekly sync automation..."
echo "=========================================="
echo ""

onlinecampus/bin/python weekly_sync.py

echo ""
echo "=========================================="
echo "Script completed!"
echo "=========================================="
