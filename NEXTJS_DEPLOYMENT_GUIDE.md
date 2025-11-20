# Next.js Web App - Complete Setup & Deployment Guide

## What You Have
All the Next.js files are ready in the `nextjs-files/` directory:
- ✅ Complete authentication system (login/signup)
- ✅ Dashboard with stats and alerts
- ✅ Ready-to-submit applications queue
- ✅ Profile page with resume upload and preferences
- ✅ API client with all backend endpoints
- ✅ TypeScript types
- ✅ Tailwind CSS styling
- ✅ Responsive design (works on mobile)

---

## Quick Start (5 minutes)

### Step 1: Create Next.js App

```bash
# From the assignment-calendar-sync directory
npx create-next-app@latest web \
  --typescript \
  --tailwind \
  --app \
  --import-alias "@/*" \
  --no-src-dir

cd web
```

### Step 2: Install Dependencies

```bash
npm install axios
```

### Step 3: Copy All Files

```bash
# Copy lib files
mkdir -p lib
cp ../nextjs-files/lib-api.ts ./lib/api.ts
cp ../nextjs-files/lib-types.ts ./lib/types.ts

# Copy contexts
mkdir -p contexts
cp ../nextjs-files/contexts-AuthContext.tsx ./contexts/AuthContext.tsx

# Copy app files
cp ../nextjs-files/app-layout.tsx ./app/layout.tsx
cp ../nextjs-files/app-page.tsx ./app/page.tsx
cp ../nextjs-files/globals.css ./app/globals.css

# Copy login page
mkdir -p app/login
cp ../nextjs-files/app-login-page.tsx ./app/login/page.tsx

# Copy signup page
mkdir -p app/signup
cp ../nextjs-files/app-signup-page.tsx ./app/signup/page.tsx

# Copy dashboard
mkdir -p app/dashboard
cp ../nextjs-files/app-dashboard-page.tsx ./app/dashboard/page.tsx

# Copy ready-to-submit page
mkdir -p app/ready
cp ../nextjs-files/app-ready-page.tsx ./app/ready/page.tsx

# Copy profile page
mkdir -p app/profile
cp ../nextjs-files/app-profile-page.tsx ./app/profile/page.tsx
```

### Step 4: Create Environment File

```bash
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF
```

### Step 5: Test Locally

```bash
# Terminal 1: Start backend (if not already running)
cd ../backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd ../web
npm run dev
```

Open http://localhost:3000 in your browser!

---

## What Each Page Does

### Landing Page (/)
- Automatically redirects to /login if not authenticated
- Redirects to /dashboard if already logged in

### Login (/login)
- Email + password authentication
- Error handling with user-friendly messages
- Link to signup page

### Signup (/signup)
- Create new account with email, password, full name
- Password validation (min 8 characters)
- Auto-login after registration

### Dashboard (/dashboard)
- Overview stats: total applications, interviews, offers
- **Big alert** when applications are ready to submit
- Top 5 job matches with match scores
- Quick navigation to profile and ready queue

### Ready to Submit (/ready)
- List of all prepared applications
- Show AI-generated cover letter
- Job details (title, company, location, salary)
- One-tap submit or dismiss buttons
- Real-time status updates

### Profile (/profile)
- Resume upload (PDF, max 5MB)
- Job preferences form:
  - Desired job titles
  - Desired locations
  - Minimum salary
  - Years of experience
  - Skills
- Usage statistics (cover letters remaining)
- "How it works" explanation

---

## Deploy to Vercel (FREE hosting!)

### Prerequisites
1. Your backend must be deployed to Railway first
2. Get your Railway backend URL (e.g., https://your-app.up.railway.app)

### Deploy Steps

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy (from the web/ directory)
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? college-assistant-web (or your choice)
# - Directory? ./ (current directory)
# - Override settings? No

# After deployment, you'll get a URL like:
# https://college-assistant-web.vercel.app
```

### Set Environment Variable in Vercel

After deployment, you need to set the backend URL:

1. Go to https://vercel.com/dashboard
2. Click on your project
3. Go to Settings > Environment Variables
4. Add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend.up.railway.app/api/v1`
   - Environments: Production, Preview, Development
5. Click "Save"
6. Go to Deployments tab
7. Click "Redeploy" on the latest deployment

---

## Testing Your Deployment

### 1. Test Authentication
```bash
# Visit your Vercel URL
# Click "Sign up"
# Create an account
# Verify you're redirected to dashboard
```

### 2. Test Profile Setup
```bash
# Click "Profile" in navbar
# Upload a PDF resume
# Fill in job preferences
# Click "Save Preferences"
# Verify success message
```

### 3. Test Dashboard
```bash
# Go back to dashboard
# Verify stats show up
# If no applications yet, that's normal - the cron runs at 8 AM daily
```

### 4. Manually Trigger Job Search (testing only)
```bash
# Using your Railway backend URL
curl -X POST https://your-backend.up.railway.app/api/v1/career/jobs/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Get your token from browser:
# 1. Open browser dev tools (F12)
# 2. Go to Application > Local Storage
# 3. Find 'access_token'
# 4. Copy the value
```

---

## Sharing with Friends

Once deployed, just send your friends the Vercel URL:

```
Hey! Check out this job application assistant I built:
https://college-assistant-web.vercel.app

Just sign up with your email and:
1. Upload your resume (PDF)
2. Set your job preferences
3. The system will automatically find jobs and prepare applications for you daily
4. You just review and submit!

You get 10 free AI cover letters per month.
```

---

## Architecture Overview

```
┌─────────────────┐
│   Next.js Web   │  (Vercel - FREE)
│   - React UI    │
│   - Auth        │  https://your-app.vercel.app
│   - Dashboard   │
└────────┬────────┘
         │
         │ HTTP Requests
         │
┌────────▼────────┐
│  FastAPI Backend│  (Railway - ~$20-30/month)
│  - Job scraping │
│  - AI cover     │  https://your-backend.up.railway.app
│  - Database     │
└────────┬────────┘
         │
         │
┌────────▼────────┐
│   PostgreSQL    │  (Railway - included)
│   - User data   │
│   - Jobs        │
│   - Applications│
└─────────────────┘
```

---

## Troubleshooting

### "API request failed" errors
**Problem:** Frontend can't reach backend
**Solution:** Check your `.env.local` (local) or Vercel environment variables (production) have the correct `NEXT_PUBLIC_API_URL`

### "Unauthorized" errors
**Problem:** Token expired or invalid
**Solution:** Log out and log back in

### Resume upload fails
**Problem:** File too large or wrong format
**Solution:** Ensure PDF format and < 5MB

### No jobs appearing
**Problem:** Cron hasn't run yet
**Solution:** Wait until 8 AM next day, or manually trigger with the curl command above

### CORS errors
**Problem:** Backend rejecting frontend requests
**Solution:** Ensure backend CORS settings include your Vercel domain:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Cost Breakdown

| Service | Cost | What It Does |
|---------|------|--------------|
| Vercel | FREE | Hosts your Next.js web app |
| Railway PostgreSQL | ~$5/month | Database for users/jobs |
| Railway Compute | ~$15-25/month | Runs your Python backend |
| OpenAI API | ~$0.50-2/month | Generates cover letters (depends on usage) |
| **Total** | **~$20-30/month** | Full working system for you + 5 friends |

---

## Next Steps

1. **Test everything locally first** - Make sure login, signup, and navigation work
2. **Deploy backend to Railway** - Follow the backend deployment guide
3. **Deploy frontend to Vercel** - Use the steps above
4. **Update CORS in backend** - Add your Vercel URL
5. **Test production** - Try signing up on your live site
6. **Share with friends** - Send them the link!

---

## Advanced: Custom Domain (Optional)

Want `college-assistant.com` instead of `college-assistant-web.vercel.app`?

1. Buy domain from Namecheap/GoDaddy (~$10-15/year)
2. In Vercel dashboard:
   - Go to Settings > Domains
   - Add your custom domain
   - Follow DNS configuration instructions
3. Update backend CORS to include new domain

---

## Monitoring & Maintenance

### Check if cron is running
```bash
# SSH into Railway (or check logs in Railway dashboard)
# Look for logs like:
# "Starting daily job search for user X"
# "Found Y new jobs for user X"
```

### Monitor usage
- Check Railway dashboard for compute/memory usage
- Check OpenAI dashboard for API usage
- Monitor PostgreSQL storage in Railway

### Update code
```bash
# Pull latest changes
git pull

# For frontend changes:
cd web
vercel --prod  # Redeploy to Vercel

# For backend changes:
git push  # Railway auto-deploys on push
```

---

## You're All Set!

Your complete job application assistant web app is ready to deploy. The system will:
- ✅ Search for jobs daily at 8 AM
- ✅ Generate personalized cover letters with AI
- ✅ Prepare applications automatically
- ✅ Notify users when applications are ready
- ✅ Allow one-tap submission

Questions? Check the troubleshooting section or reach out for help!
