#!/bin/bash
# Script to create a standalone Assignment Calendar Sync app for distribution

echo "=========================================="
echo "📦 Building Assignment Calendar Sync App"
echo "=========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js from https://nodejs.org"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js which includes npm"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r python/requirements.txt

# Create build directory structure
echo "📁 Preparing build files..."
mkdir -p build

# Create a simple icon if one doesn't exist
if [ ! -f "build/icon.png" ]; then
    echo "🎨 Creating app icon..."
    # For now, just create a placeholder - in real app you'd have proper icons
    touch build/icon.png
    touch build/icon.icns
    touch build/icon.ico
fi

# Build the app for current platform
echo "🔨 Building app for $(uname -s)..."

case "$(uname -s)" in
    Darwin)
        echo "Building for macOS..."
        npm run build:mac
        ;;
    Linux)
        echo "Building for Linux..."
        npm run build:linux
        ;;
    MINGW*|CYGWIN*|MSYS*)
        echo "Building for Windows..."
        npm run build:win
        ;;
    *)
        echo "⚠️  Unknown platform. Building for all platforms..."
        npm run build:all
        ;;
esac

echo ""
echo "✅ Build complete!"
echo ""
echo "📂 Built app is in the 'dist' folder:"
ls -la dist/

echo ""
echo "🎉 Your standalone Assignment Calendar Sync app is ready!"
echo "   Users can now run this app without needing to install anything else."
echo ""
echo "📋 Next steps:"
echo "   1. Test the app by running the executable in the dist folder"
echo "   2. Distribute the app to users"
echo "   3. Users just double-click to run - no setup required!"