#!/bin/bash
# setup-nextjs.sh - Automated Next.js Web App Setup
# This script creates and configures your Next.js app with all the files

set -e  # Exit on any error

echo "======================================"
echo "Next.js Web App Setup Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -d "nextjs-files" ]; then
    echo "Error: nextjs-files directory not found!"
    echo "Please run this script from the assignment-calendar-sync directory"
    exit 1
fi

echo "Step 1: Creating Next.js app..."
echo "--------------------------------------"
npx create-next-app@latest web \
  --typescript \
  --tailwind \
  --app \
  --import-alias "@/*" \
  --no-src-dir \
  --no-git

cd web

echo ""
echo "Step 2: Installing dependencies..."
echo "--------------------------------------"
npm install axios

echo ""
echo "Step 3: Creating directory structure..."
echo "--------------------------------------"
mkdir -p lib contexts app/login app/signup app/dashboard app/ready app/profile

echo ""
echo "Step 4: Copying files..."
echo "--------------------------------------"

# Copy lib files
echo "  - Copying lib/api.ts"
cp ../nextjs-files/lib-api.ts ./lib/api.ts

echo "  - Copying lib/types.ts"
cp ../nextjs-files/lib-types.ts ./lib/types.ts

# Copy contexts
echo "  - Copying contexts/AuthContext.tsx"
cp ../nextjs-files/contexts-AuthContext.tsx ./contexts/AuthContext.tsx

# Copy app files
echo "  - Copying app/layout.tsx"
cp ../nextjs-files/app-layout.tsx ./app/layout.tsx

echo "  - Copying app/page.tsx"
cp ../nextjs-files/app-page.tsx ./app/page.tsx

echo "  - Copying app/globals.css"
cp ../nextjs-files/globals.css ./app/globals.css

# Copy page files
echo "  - Copying app/login/page.tsx"
cp ../nextjs-files/app-login-page.tsx ./app/login/page.tsx

echo "  - Copying app/signup/page.tsx"
cp ../nextjs-files/app-signup-page.tsx ./app/signup/page.tsx

echo "  - Copying app/dashboard/page.tsx"
cp ../nextjs-files/app-dashboard-page.tsx ./app/dashboard/page.tsx

echo "  - Copying app/ready/page.tsx"
cp ../nextjs-files/app-ready-page.tsx ./app/ready/page.tsx

echo "  - Copying app/profile/page.tsx"
cp ../nextjs-files/app-profile-page.tsx ./app/profile/page.tsx

echo ""
echo "Step 5: Creating environment file..."
echo "--------------------------------------"
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF
echo "  - Created .env.local"

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Your Next.js app is ready in the 'web' directory!"
echo ""
echo "To start development:"
echo "  1. Start your backend (in another terminal):"
echo "     cd backend"
echo "     source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  2. Start the frontend:"
echo "     cd web"
echo "     npm run dev"
echo ""
echo "  3. Open http://localhost:3000 in your browser"
echo ""
echo "To deploy to Vercel:"
echo "  cd web"
echo "  npm i -g vercel"
echo "  vercel"
echo ""
echo "See NEXTJS_DEPLOYMENT_GUIDE.md for full deployment instructions!"
echo ""
