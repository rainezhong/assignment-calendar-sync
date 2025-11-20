#!/bin/bash

# ============================================
# Create Web App - Quick Start Script
# ============================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "🌐 Creating College Assistant Web App"
echo "=========================================="
echo ""

# Check if web directory already exists
if [ -d "web" ]; then
    echo -e "${BLUE}⚠️  'web' directory already exists. Remove it first:${NC}"
    echo "   rm -rf web"
    exit 1
fi

# Create Vite React TypeScript app
echo -e "${BLUE}[1/5] Creating Vite + React + TypeScript project...${NC}"
npm create vite@latest web -- --template react-ts
cd web

# Install dependencies
echo ""
echo -e "${BLUE}[2/5] Installing dependencies...${NC}"
npm install

# Install additional packages
echo ""
echo -e "${BLUE}[3/5] Installing additional packages...${NC}"
npm install axios react-router-dom @tanstack/react-query

# Install Tailwind CSS
echo ""
echo -e "${BLUE}[4/5] Setting up Tailwind CSS...${NC}"
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create .env file
echo ""
echo -e "${BLUE}[5/5] Creating environment files...${NC}"
cat > .env.local << 'EOF'
# API URL - Update this after deploying backend
VITE_API_URL=http://localhost:8000/api/v1
EOF

cat > .env.production << 'EOF'
# Production API URL - Update with your Railway URL
VITE_API_URL=https://your-backend.up.railway.app/api/v1
EOF

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Web app created successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Update Tailwind config:"
echo "   cat WEB_TAILWIND_CONFIG.txt > web/tailwind.config.js"
echo ""
echo "2. Copy web app components:"
echo "   # I'll provide these in separate files"
echo ""
echo "3. Start development server:"
echo "   cd web"
echo "   npm run dev"
echo ""
echo "4. Build for production:"
echo "   npm run build"
echo ""
echo "5. Deploy to Vercel (FREE):"
echo "   npm i -g vercel"
echo "   vercel"
echo ""
