⏺ Step 1: Deploy Backend to Railway (30 min)

  1. Sign up for Railway:
    - Go to https://railway.app
    - Sign up with GitHub (free $5 credit)
  2. Create new project:
    - Click "New Project"
    - Select "Deploy from GitHub repo"
    - Choose your assignment-calendar-sync repo
  3. Add PostgreSQL database:
    - In Railway project, click "+ New"
    - Select "Database" → "PostgreSQL"
    - Wait ~2 min for provisioning
  4. Configure backend service:
    - Click on your backend service
    - Go to "Settings" tab
    - Set Root Directory: backend
    - Set Build Command: pip install -r requirements.txt
    - Set Start Command: uvicorn app.main:app --host 0.0.0.0 --port 
  $PORT
  5. Add environment variables:
    - Click "Variables" tab
    - Click "Raw Editor"
    - Paste:
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  SECRET_KEY=96uP90_MGtGBWPEqeK0vxDmNHadDPz-NdyNSQev4xGU
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  GEMINI_API_KEY=AIzaSyBaWkmLKwdsKhveQjbZWFpm2EoyqE_ygHc
  DEBUG=False
  ALLOWED_ORIGINS=["*"]
  PROJECT_NAME=College Assistant
  VERSION=1.0.0
  ENABLE_BACKGROUND_JOBS=True
  JOB_SEARCH_HOUR=8
  JOB_SEARCH_MINUTE=0
  6. Generate public domain:
    - Go to "Settings" → "Networking"
    - Click "Generate Domain"
    - Copy URL (e.g., https://your-app.up.railway.app)
  7. Run migrations:
  cd backend
  export DATABASE_URL="<paste PostgreSQL URL from Railway>"
  alembic upgrade head

  Step 2: Set Up Next.js Web App (15 min)

  # Create Next.js app
  npx create-next-app@latest web --typescript --tailwind --app
  --no-git

  # Move your pre-built files into the web directory
  cd web
  cp ../nextjs-files/lib-api.ts src/lib/api.ts
  cp ../nextjs-files/lib-types.ts src/lib/types.ts
  cp ../nextjs-files/contexts-AuthContext.tsx
  src/contexts/AuthContext.tsx
  cp ../nextjs-files/globals.css src/app/globals.css
  cp ../nextjs-files/app-*.tsx src/app/

  # Create .env.local with your Railway backend URL
  echo "NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api/v1"
  > .env.local

  # Install dependencies
  npm install axios

  # Test locally
  npm run dev

  Step 3: Deploy Frontend to Vercel (10 min - FREE!)

  # Install Vercel CLI
  npm i -g vercel

  # Deploy from web directory
  cd web
  vercel

  # Follow prompts:
  # - Link to Vercel account? Yes
  # - Set up and deploy? Yes
  # - Environment variable NEXT_PUBLIC_API_URL? (paste Railway URL)

  Your app will be live at https://your-app.vercel.app

  Step 4: Share with Friends

  Send them a message like:

  Hey! I built a web app that auto-applies to jobs with AI-generated
   cover letters. Want to try it?

  Just go to: https://your-app.vercel.app

  1. Sign up
  2. Upload your resume
  3. Set job preferences
  4. Check back tomorrow - jobs will be auto-matched and ready to 
  submit!

  Works on phone/desktop. Let me know if you hit any issues!

  ---
  Quick Wins

  You're using Gemini instead of OpenAI - that's smart! It's
  cheaper. Your costs will be:
  - Railway (backend + DB): ~$20-30/month
  - Vercel (frontend): FREE
  - Gemini API: ~$1-5/month
  - Total: $21-35/month (~$4-7 per person with 5 friends)

  Want me to help you with any specific step? I can:
  - Walk you through the Railway deployment
  - Help set up the Next.js app
  - Debug any issues that come up

  Todos
  ☐ Deploy backend to Railway and set up PostgreSQL database
  ☐ Configure backend environment variables in Railway
  ☐ Run database migrations on Railway
  ☐ Set up Next.js web app from nextjs-files/
  ☐ Deploy frontend to Vercel
  ☐ Test the full app flow end-to-end
  ☐ Share with friends