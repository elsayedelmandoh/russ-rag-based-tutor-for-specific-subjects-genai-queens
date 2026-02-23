#!/bin/bash
# RUSS RAG Tutor - Quick Setup Script
# Run this script to set up and start the RUSS application

set -e  # Exit on error

# Step 1: Python environment
echo "[1/5] Checking Python environment..."
if ! command -v python &> /dev/null; then
    echo "❌ Python 3.9+ is required but not found"
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Step 2: Install dependencies
echo ""
echo "[2/5] Installing Python dependencies..."
python -m pip install --quiet -r requirements.txt
echo "✓ Dependencies installed"

# Step 3: Create data directories
echo ""
echo "[3/5] Creating data directories..."
mkdir -p data/chromadb
mkdir -p data/uploads
mkdir -p data/curriculum
echo "✓ Data directories created"

# Step 4: Validate imports
echo ""
echo "[4/5] Validating application setup..."
python validate.py
echo ""

# Step 5: Instructions
echo "[5/5] Setup complete!"
echo ""
echo "✓ RUSS is ready to run!"
echo ""
echo "Next steps:"
echo ""
echo "1. In a new terminal, start Ollama:"
echo "   $ ollama serve"
echo ""
echo "2. In another terminal, pull the required models (first time only):"
echo "   $ ollama pull llama3.2 nomic-embed-text llama-guard3:1b"
echo ""
echo "3. Then start the application:"
echo "   $ streamlit run app.py"
echo ""
echo "4. Open http://localhost:8501 in your browser"
echo ""
echo "For help, see README.md"
