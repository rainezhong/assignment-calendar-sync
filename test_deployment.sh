#!/bin/bash

# ============================================
# Deployment Verification Script
# Tests that your API is working correctly
# ============================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide your API URL${NC}"
    echo "Usage: ./test_deployment.sh https://your-app.up.railway.app"
    exit 1
fi

API_URL="$1"
BASE_URL="${API_URL}/api/v1"

echo ""
echo "=========================================="
echo "Testing Deployment: $API_URL"
echo "=========================================="
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s "${API_URL}/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "  Response: $HEALTH"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "  Response: $HEALTH"
    exit 1
fi
echo ""

# Test 2: API Root
echo -e "${YELLOW}Test 2: API Root${NC}"
ROOT=$(curl -s "${API_URL}/")
if echo "$ROOT" | grep -q "College Assistant"; then
    echo -e "${GREEN}✓ API root accessible${NC}"
    echo "  Response: $ROOT"
else
    echo -e "${RED}✗ API root failed${NC}"
    echo "  Response: $ROOT"
fi
echo ""

# Test 3: OpenAPI Docs
echo -e "${YELLOW}Test 3: OpenAPI Documentation${NC}"
DOCS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/docs")
if [ "$DOCS" = "200" ]; then
    echo -e "${GREEN}✓ API docs accessible${NC}"
    echo "  URL: ${BASE_URL}/docs"
else
    echo -e "${RED}✗ API docs failed (HTTP $DOCS)${NC}"
fi
echo ""

# Test 4: User Registration
echo -e "${YELLOW}Test 4: User Registration${NC}"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="testpass123"

REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"full_name\": \"Test User\"}")

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    echo -e "${GREEN}✓ User registration works${NC}"
    echo "  Created test user: $TEST_EMAIL"
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "  Response: $REGISTER_RESPONSE"
    exit 1
fi
echo ""

# Test 5: User Login
echo -e "${YELLOW}Test 5: User Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ User login works${NC}"
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "  Got access token: ${ACCESS_TOKEN:0:20}..."
else
    echo -e "${RED}✗ User login failed${NC}"
    echo "  Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 6: Protected Endpoint (Get Current User)
echo -e "${YELLOW}Test 6: Protected Endpoint (Auth Check)${NC}"
ME_RESPONSE=$(curl -s "${BASE_URL}/auth/me" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$ME_RESPONSE" | grep -q "$TEST_EMAIL"; then
    echo -e "${GREEN}✓ Authentication working${NC}"
    echo "  User: $TEST_EMAIL"
else
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "  Response: $ME_RESPONSE"
    exit 1
fi
echo ""

# Test 7: Career Endpoints Exist
echo -e "${YELLOW}Test 7: Career Endpoints${NC}"
PROFILE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/career/profile" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$PROFILE_RESPONSE" = "404" ]; then
    echo -e "${GREEN}✓ Career endpoints accessible (expected 404 - no profile yet)${NC}"
elif [ "$PROFILE_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Career endpoints accessible${NC}"
else
    echo -e "${YELLOW}⚠ Career endpoint returned HTTP $PROFILE_RESPONSE${NC}"
fi
echo ""

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓ All Critical Tests Passed!${NC}"
echo "=========================================="
echo ""
echo "Your deployment is working! 🎉"
echo ""
echo "Next steps:"
echo "1. Share this URL with friends: $API_URL"
echo "2. Update mobile app API_BASE_URL to: $BASE_URL"
echo "3. Test mobile app with Expo Go"
echo ""
echo "Useful URLs:"
echo "  API Docs: ${BASE_URL}/docs"
echo "  Health Check: ${API_URL}/health"
echo ""
