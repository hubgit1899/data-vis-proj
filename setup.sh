#!/bin/bash
# Setup script for macOS/Linux
# Run with: bash setup.sh

echo "================================"
echo "  Traffic Safety Analysis Setup"
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================"
echo "  Setup Complete! ✓"
echo "================================"
echo ""
echo "To run the analysis:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the analysis script:"
echo "     python analysis-code/analysis_report_v2.py"
echo ""
echo "  3. Check the 'output/' folder for generated visualizations."
echo ""
