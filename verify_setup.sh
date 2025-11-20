#!/bin/bash

# ============================================
# Setup Verification Script
# Checks that everything is ready to deploy
# ============================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "🔍 College Assistant - Setup Verification"
echo "=========================================="
echo ""

ERRORS=0

# Check 1: Python version
echo -e "${BLUE}[1/10] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 2: Node.js version
echo -e "${BLUE}[2/10] Checking Node.js version...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js installed: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Backend dependencies
echo -e "${BLUE}[3/10] Checking backend dependencies...${NC}"
if [ -f "backend/requirements.txt" ]; then
    echo -e "${GREEN}✓ requirements.txt found${NC}"

    # Check if key packages exist
    if grep -q "fastapi" backend/requirements.txt && \
       grep -q "sqlalchemy" backend/requirements.txt && \
       grep -q "openai" backend/requirements.txt; then
        echo -e "${GREEN}✓ Key packages listed${NC}"
    else
        echo -e "${YELLOW}⚠ Some packages might be missing${NC}"
    fi
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 4: Mobile dependencies
echo -e "${BLUE}[4/10] Checking mobile dependencies...${NC}"
if [ -f "mobile/package.json" ]; then
    echo -e "${GREEN}✓ package.json found${NC}"

    # Check if node_modules exists
    if [ -d "mobile/node_modules" ]; then
        echo -e "${GREEN}✓ node_modules installed${NC}"
    else
        echo -e "${YELLOW}⚠ node_modules not installed (run: cd mobile && npm install)${NC}"
    fi
else
    echo -e "${RED}✗ package.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 5: Environment file
echo -e "${BLUE}[5/10] Checking environment configuration...${NC}"
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"

    # Check for critical variables
    if grep -q "SECRET_KEY=CHANGE-THIS" backend/.env; then
        echo -e "${RED}✗ SECRET_KEY not set! Run: python backend/generate_secret_key.py${NC}"
        ERRORS=$((ERRORS + 1))
    elif grep -q "SECRET_KEY=" backend/.env; then
        echo -e "${GREEN}✓ SECRET_KEY is set${NC}"
    fi

    if grep -q "OPENAI_API_KEY=sk-" backend/.env; then
        echo -e "${GREEN}✓ OPENAI_API_KEY is set${NC}"
    else
        echo -e "${YELLOW}⚠ OPENAI_API_KEY not set (needed for AI cover letters)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ .env file not found (copy from .env.example)${NC}"
fi
echo ""

# Check 6: Database migrations
echo -e "${BLUE}[6/10] Checking database migrations...${NC}"
if [ -d "backend/alembic/versions" ]; then
    VERSION_COUNT=$(ls -1 backend/alembic/versions/*.py 2>/dev/null | wc -l)
    if [ $VERSION_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓ Migration files exist ($VERSION_COUNT migrations)${NC}"
    else
        echo -e "${YELLOW}⚠ No migration files found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Alembic versions directory not found${NC}"
fi
echo ""

# Check 7: Models
echo -e "${BLUE}[7/10] Checking database models...${NC}"
if [ -f "backend/app/models/career.py" ]; then
    echo -e "${GREEN}✓ Career models found${NC}"

    # Check for usage limits fields
    if grep -q "cover_letters_generated" backend/app/models/career.py && \
       grep -q "cover_letter_limit" backend/app/models/career.py; then
        echo -e "${GREEN}✓ Usage limit fields added${NC}"
    else
        echo -e "${YELLOW}⚠ Usage limit fields might be missing${NC}"
    fi
else
    echo -e "${RED}✗ Career models not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 8: Mobile screens
echo -e "${BLUE}[8/10] Checking mobile screens...${NC}"
if [ -f "mobile/src/screens/CareerHubScreen.tsx" ] && \
   [ -f "mobile/src/screens/ReadyToSubmitScreen.tsx" ]; then
    echo -e "${GREEN}✓ Career screens found${NC}"
else
    echo -e "${RED}✗ Career screens missing${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 9: API service
echo -e "${BLUE}[9/10] Checking mobile API service...${NC}"
if [ -f "mobile/src/services/api.ts" ]; then
    echo -e "${GREEN}✓ API service found${NC}"

    # Check for career endpoints
    if grep -q "getReadyToSubmitQueue" mobile/src/services/api.ts && \
       grep -q "approveApplication" mobile/src/services/api.ts; then
        echo -e "${GREEN}✓ Career endpoints implemented${NC}"
    else
        echo -e "${YELLOW}⚠ Some career endpoints might be missing${NC}"
    fi
else
    echo -e "${RED}✗ API service not found${NC}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 10: Documentation
echo -e "${BLUE}[10/10] Checking documentation...${NC}"
if [ -f "DEPLOY_TODAY.md" ] && \
   [ -f "START_HERE.md" ] && \
   [ -f "FRIEND_ONBOARDING.md" ]; then
    echo -e "${GREEN}✓ Deployment guides found${NC}"
else
    echo -e "${YELLOW}⚠ Some guides might be missing${NC}"
fi
echo ""

# Summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo "=========================================="
    echo ""
    echo "You're ready to deploy! Next steps:"
    echo ""
    echo "1. Generate SECRET_KEY:"
    echo "   python backend/generate_secret_key.py"
    echo ""
    echo "2. Copy to .env:"
    echo "   cp backend/.env.example backend/.env"
    echo "   # Then edit backend/.env with your keys"
    echo ""
    echo "3. Follow deployment guide:"
    echo "   cat START_HERE.md"
    echo "   cat DEPLOY_TODAY.md"
    echo ""
else
    echo -e "${RED}❌ FOUND $ERRORS ERROR(S)${NC}"
    echo "=========================================="
    echo ""
    echo "Please fix the errors above before deploying."
    echo ""
fi
