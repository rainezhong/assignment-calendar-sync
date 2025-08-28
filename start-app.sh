#!/bin/bash

# Assignment Calendar Sync - Desktop App Startup Script

echo "🚀 Starting Assignment Calendar Sync Desktop App..."
echo "=================================================="

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+ first."
    echo "   Download from: https://python.org/"
    exit 1
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node.js dependencies"
        exit 1
    fi
fi

# Install Python dependencies if needed
if [ ! -d "python/venv" ]; then
    echo "🐍 Setting up Python virtual environment..."
    cd python
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Python dependencies installation failed, but continuing..."
        echo "   You may need to install them manually:"
        echo "   cd python && pip3 install -r requirements.txt"
    fi
fi

# Start the Electron app
echo "✅ Starting desktop app..."
echo ""

if [ "$1" = "dev" ]; then
    echo "🔧 Starting in development mode..."
    npm run electron-dev
else
    echo "🎯 Starting in production mode..."
    npm run electron
fi