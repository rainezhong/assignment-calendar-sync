#!/bin/bash
# One-click script to run Assignment Calendar Sync

echo "======================================"
echo "📚 ASSIGNMENT CALENDAR SYNC"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python first."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "First time setup detected!"
    echo "Let's configure your settings..."
    echo ""
    python3 setup.py
    
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please try again."
        exit 1
    fi
fi

# Check if dependencies are installed
python3 -c "import selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install selenium requests python-dotenv pytz python-dateutil
fi

# Run the sync
echo ""
echo "Starting assignment sync..."
echo "------------------------------"
python3 python/simple_sync.py

# Keep terminal open on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo ""
    echo "Press any key to exit..."
    read -n 1
fi