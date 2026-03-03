#!/bin/bash
# Vehicle Dashboard Startup Script

echo "================================================"
echo "  STM32 Vehicle Dashboard"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if STM32 is connected
echo ""
echo "🔌 Checking for STM32 board..."
if ls /dev/ttyACM* 1> /dev/null 2>&1; then
    echo "✅ STM32 board detected at $(ls /dev/ttyACM*)"
else
    echo "⚠️  Warning: No STM32 board detected"
    echo "   Please connect your STM32 board and try again"
    echo ""
fi

# Close PuTTY if running
echo ""
echo "🔍 Checking for PuTTY instances..."
if pgrep -x "putty" > /dev/null; then
    echo "⚠️  PuTTY is running. Closing it..."
    pkill putty
    sleep 1
fi

echo ""
echo "================================================"
echo "🚀 Starting Vehicle Dashboard Server..."
echo "================================================"
echo ""
echo "Dashboard will be available at:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py
