# START HERE: Your Deployment Roadmap

## ✅ What's Ready

You have a complete Auto-Prep job application system:

**Backend:**
- ✅ FastAPI with PostgreSQL
- ✅ Background job scheduler (APScheduler)
- ✅ Job scraping (LinkedIn + Indeed)
- ✅ AI job matching
- ✅ Auto cover letter generation
- ✅ **Data isolation** (users can't see each other's data)
- ✅ **Usage limits** (10 free cover letters/month per user)

**Mobile:**
- ✅ React Native with Expo
- ✅ Authentication (JWT)
- ✅ Career Hub with stats
- ✅ Ready to Submit queue
- ✅ One-tap approval

**New additions (just implemented):**
- ✅ Usage tracking fields in UserProfile model
- ✅ Monthly usage reset logic
- ✅ Automatic fallback to template cover letters when limit hit

---

## 🎯 Your Goal

**Scenario 1 → Scenario 2 Path:**

1. **Today:** Get 5 friends testing via Expo Go ($25/month)
2. **Next Week:** Upgrade to TestFlight for professional feel ($40/month)
3. **Month 2+:** Scale to 20 friends, split costs ($2/person/month)

---

## 📋 Today's Checklist (3 Hours)

Follow **DEPLOY_TODAY.md** step by step:

### ⏰ Hour 1: Security & Setup (CRITICAL)
- [ ] Run database migration for usage limits:
  ```bash
  cd backend
  alembic revision --autogenerate -m "Add usage limits and data isolation"
  alembic upgrade head
  ```

- [ ] Sign up for Railway (https://railway.app)
- [ ] Sign up for OpenAI (https://platform.openai.com)
- [ ] Add $10 credit to OpenAI

### ⏰ Hour 2: Deploy Backend
- [ ] Create Railway project from GitHub
- [ ] Add PostgreSQL database
- [ ] Set environment variables in Railway:
  ```
  DATABASE_URL (from PostgreSQL service)
  SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
  OPENAI_API_KEY (from OpenAI)
  ```
- [ ] Set build settings (root: backend, start: uvicorn app.main:app --host 0.0.0.0 --port $PORT)
- [ ] Generate domain (Settings → Networking)
- [ ] Run migrations against Railway DB

### ⏰ Hour 3: Mobile & Testing
- [ ] Update `mobile/src/services/api.ts` with Railway URL
- [ ] Test: `cd mobile && npx expo start`
- [ ] Download Expo Go on your phone
- [ ] Test sign up, login, resume upload
- [ ] Send QR code to 5 friends
- [ ] Help first 2 friends get set up

---

## 📱 Next Week: TestFlight Upgrade

Follow **DEPLOY_NEXT_WEEK.md** for:

- [ ] Build iOS app with EAS
- [ ] Submit to TestFlight
- [ ] Invite 10-20 friends
- [ ] Add push notifications
- [ ] Implement invite codes
- [ ] Set up cost sharing

---

## 📊 What to Monitor

### Today (First 24 Hours)
- Can friends sign up?
- Can they upload resumes?
- Does Railway backend stay up?
- Any errors in Railway logs?

**Check:** Railway Dashboard → Deployments → View Logs

### This Week
- How many sign-ups? (Target: 5)
- How many resumes uploaded? (Target: 4+)
- Are background jobs running? (Check at 8 AM tomorrow)
- OpenAI costs? (Should be <$5)

**Check:**
- Railway: https://railway.app/project/YOUR_PROJECT
- OpenAI: https://platform.openai.com/usage

### Costs (First Month)
- Railway: $20-30
- OpenAI: $5-15
- **Total: $25-45** ($5-9 per person with 5 friends)

---

## 🆘 Quick Troubleshooting

### Backend won't deploy
- **Check:** Railway logs for errors
- **Common issue:** DATABASE_URL not set
- **Fix:** Copy from PostgreSQL service → Connect → DATABASE_URL

### Mobile can't connect
- **Check:** API_BASE_URL in api.ts
- **Common issue:** Using localhost instead of Railway URL
- **Fix:** Must be https://your-app.up.railway.app/api/v1

### Cover letters not generating
- **Check:** OpenAI API key set in Railway
- **Check:** OpenAI credits: https://platform.openai.com/account/billing
- **Fix:** Add $10 credit

### Background jobs not running
- **Check:** Railway logs at 8 AM
- **Expected:** Might not work perfectly on Railway (free tier restarts)
- **Fix:** Manually trigger for MVP: `POST /career/jobs/search` via API

### Friends hit "usage limit exceeded"
- **Expected:** After 10 cover letters, they get template cover letters
- **Not an error:** This is working as designed
- **Fix:** Increase limit in code or have them wait 30 days for reset

---

## 📚 Documentation Structure

```
START_HERE.md (this file)       ← Overview & quick start
DEPLOY_TODAY.md                 ← Detailed steps for Scenario 1 (Expo Go)
DEPLOY_NEXT_WEEK.md             ← Upgrade to Scenario 2 (TestFlight)

FRIEND_GROUP_DEPLOYMENT_GUIDE.md ← Full analysis (8 decisions)
DECISION_WORKSHEET.md           ← Quick decision tool

AUTO_PREP_SYSTEM.md            ← Technical documentation
AUTO_PREP_INTEGRATION_COMPLETE.md ← What was built

QUICK_START_AUTO_PREP.md       ← General setup guide
APP_STORE_DEPLOYMENT_GUIDE.md  ← If you want App Store later
```

**Your path:** START_HERE → DEPLOY_TODAY → DEPLOY_NEXT_WEEK

---

## ✅ Readiness Check

Before deploying, you have:

- [x] Backend with data isolation (**implemented**)
- [x] Usage limits to control costs (**implemented**)
- [x] Mobile app with Career Hub (**implemented**)
- [x] Ready to Submit screen (**implemented**)
- [x] Background job scheduler (**implemented**)
- [x] Deployment guide (DEPLOY_TODAY.md) (**ready**)
- [x] Apple Developer account (**you have it**)
- [x] Comfortable with terminal (**yes**)

**You're ready to deploy!** 🚀

---

## 🎯 Your Action: Start DEPLOY_TODAY.md Now

Open **DEPLOY_TODAY.md** and follow it step by step. It's written for someone with your technical level and goals.

**Timeline:**
- Today: 3 hours → Working app for 5 friends
- Next week: 1 day → TestFlight upgrade
- Month 2: Iterate based on feedback

**Cost:**
- Today: $25/month ($5/person with 5 friends)
- Week 2: $40/month ($2/person with 20 friends)

---

## 💬 Questions?

Common questions answered in:

1. **"How do I...?"** → DEPLOY_TODAY.md has step-by-step commands
2. **"What if...?"** → Troubleshooting section in DEPLOY_TODAY.md
3. **"Should I...?"** → DECISION_WORKSHEET.md helps you decide
4. **"What about...?"** → FRIEND_GROUP_DEPLOYMENT_GUIDE.md has full analysis

---

## 🎉 Good Luck!

You have everything you need. The hard work (building the system) is done.

Now it's just:
1. Deploy to Railway (30 min)
2. Test on your phone (15 min)
3. Invite 5 friends (15 min)

Then iterate based on their feedback!

**Ready? Go to DEPLOY_TODAY.md and start! →**
