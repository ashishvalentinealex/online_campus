#!/bin/bash

echo "=========================================="
echo "Online Campus Weekly Sync - Setup & Run"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "onlinecampus" ]; then
    echo "[1/6] Creating virtual environment..."
    python3 -m venv onlinecampus
    echo "✅ Virtual environment created"
else
    echo "[1/6] Virtual environment already exists"
fi

echo ""
echo "[2/6] Installing/Updating dependencies..."
onlinecampus/bin/pip install -q --upgrade pip
onlinecampus/bin/pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "[3/6] Running weekly sync (extract new records)..."
echo "=========================================="
echo ""
onlinecampus/bin/python weekly_sync.py

echo ""
echo "[4/6] Enriching data with OpenAI..."
echo "=========================================="
onlinecampus/bin/python enrich_data.py

echo ""
echo "[5/6] Cleaning phone numbers..."
echo "=========================================="
onlinecampus/bin/python clean_phones.py

echo ""
echo "[6/6] Uploading to Google Sheets, sending VCF & welcome emails..."
echo "=========================================="
onlinecampus/bin/python upload_to_sheets.py

echo ""
echo "=========================================="
echo "Script completed!"
echo "=========================================="
