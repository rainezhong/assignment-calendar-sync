# Deployment Commands - Quick Reference

Copy-paste commands you'll need. Keep this file open during deployment!

---

## 🚀 Before You Start

```bash
# Verify everything is ready
./verify_setup.sh

# Generate SECRET_KEY
python backend/generate_secret_key.py
```

---

## 📦 Initial Setup

```bash
# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your keys (SECRET_KEY, OPENAI_API_KEY, DATABASE_URL)

# Run database migrations
cd backend
alembic revision --autogenerate -m "Add usage limits and career features"
alembic upgrade head
```

---

## 🧪 Local Testing

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Seed test data
cd backend
python seed_test_data.py

# Terminal 3: Start mobile
cd mobile
npx expo start

# Test API
curl http://localhost:8000/health
```

---

## ☁️ Railway Deployment

### Deploy Backend:
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Add PostgreSQL database (click "New" → "Database" → "PostgreSQL")
5. Set environment variables (see below)
6. Generate domain (Settings → Networking → Generate Domain)

### Environment Variables for Railway:
```bash
# Copy these into Railway → Backend Service → Variables

DATABASE_URL=  # Copy from PostgreSQL service → Connect tab
SECRET_KEY=    # Generate with: python backend/generate_secret_key.py
OPENAI_API_KEY=sk-your-key-here
ENABLE_BACKGROUND_JOBS=True
JOB_SEARCH_HOUR=8
JOB_SEARCH_MINUTE=0
ALLOWED_ORIGINS=["*"]
DEBUG=False
```

### Run Migrations on Railway:
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link
railway login
railway link

# Run migrations
railway run alembic upgrade head
```

### Test Deployment:
```bash
./test_deployment.sh https://your-app.up.railway.app
```

---

## 📱 Mobile App Setup

```bash
# Install dependencies
cd mobile
npm install

# Update API URL
# Edit: mobile/src/services/api.ts
# Change API_BASE_URL to: https://your-app.up.railway.app/api/v1

# Start Expo
npx expo start

# Clear cache if issues
npx expo start -c
```

---

## 🔍 Testing Commands

```bash
# Health check
curl https://your-app.up.railway.app/health

# Register test user
curl -X POST https://your-app.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
# Save the access_token from response!

# Get current user (test auth)
curl https://your-app.up.railway.app/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Full test suite
./test_deployment.sh https://your-app.up.railway.app
```

---

## 👥 Invite Friends

```bash
# Get Expo QR code
cd mobile
npx expo start
# QR code appears in terminal - screenshot and share!

# Or share direct link (shown in Expo output)
```

**Send them FRIEND_ONBOARDING.md** - it has complete setup instructions!

---

## 🐛 Common Issues

### Backend won't start on Railway
```bash
# Check logs: Railway → Backend Service → Deployments → View Logs
# Usually: DATABASE_URL or SECRET_KEY not set
```

### Mobile can't connect
```bash
# Check API_BASE_URL in mobile/src/services/api.ts
# Must be: https://your-app.up.railway.app/api/v1 (not localhost!)

# Restart Expo
cd mobile
npx expo start -c
```

### Cover letters not generating
```bash
# Check OpenAI key: Railway → Variables → OPENAI_API_KEY
# Check credits: https://platform.openai.com/usage
# Try GPT-3.5 instead of GPT-4 (cheaper)
```

### Background jobs not running
```bash
# Check Railway logs at 8 AM
# Manual trigger:
curl -X POST https://your-app.up.railway.app/api/v1/career/jobs/search \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Monitoring URLs

**Railway:**
- Dashboard: https://railway.app
- Logs: Railway → Backend Service → Deployments
- Usage: Railway → Backend Service → Usage

**OpenAI:**
- Usage: https://platform.openai.com/usage
- API Keys: https://platform.openai.com/api-keys

**API Docs:**
- Production: https://your-app.up.railway.app/api/v1/docs
- Local: http://localhost:8000/api/v1/docs

---

## 📋 Daily Checks

**Morning (5 min):**
```bash
# 1. Check background jobs ran
# Railway → Logs → Search for "Daily Job Search"

# 2. Check OpenAI usage
# https://platform.openai.com/usage

# 3. Test mobile app
# Open app, check if working
```

**Weekly (15 min):**
```bash
# 1. Review total costs
# Railway → Usage tab
# OpenAI → Usage page

# 2. Check friend feedback
# Any bugs or issues?

# 3. Review metrics
# How many signups? Applications? Issues?
```

---

## 🎯 Useful Scripts

```bash
# Verify setup before deploying
./verify_setup.sh

# Test deployed API
./test_deployment.sh https://your-app.up.railway.app

# Generate SECRET_KEY
python backend/generate_secret_key.py

# Seed test data
python backend/seed_test_data.py
```

---

## 💡 Pro Tips

1. **Bookmark Railway dashboard** - you'll check it often
2. **Save your API URL** - you'll use it everywhere
3. **Test locally first** - catches 90% of issues
4. **Check logs immediately** - if something fails
5. **Screenshot errors** - helps with debugging

---

## 🆘 Emergency Commands

```bash
# Restart Railway app
# Go to: Railway → Backend → Settings → Restart

# Roll back migration
cd backend
alembic downgrade -1

# Disable background jobs
# Railway → Backend → Variables → ENABLE_BACKGROUND_JOBS=False

# Check Railway status
# https://railway.statuspage.io
```

---

## ✅ Deployment Checklist

**Before deploying:**
- [ ] .env file created with all keys
- [ ] SECRET_KEY generated (not default)
- [ ] OPENAI_API_KEY added
- [ ] Migrations run locally
- [ ] Backend tested locally
- [ ] Mobile tested locally

**After deploying:**
- [ ] Railway build succeeded
- [ ] Health check passes
- [ ] Can register user
- [ ] Can login
- [ ] API docs accessible
- [ ] Mobile app connects
- [ ] Test data seeded
- [ ] Friends can access

---

**Keep this file open while deploying!** You'll reference it constantly.

For detailed steps: See **DEPLOY_TODAY.md**
For friend instructions: See **FRIEND_ONBOARDING.md**
