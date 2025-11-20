# Deployment Quickstart Guide

This guide will get your Assignment Calendar Sync app from development to production.

## 🚀 Quick Overview

You now have a complete stack:
- **Backend**: FastAPI with PostgreSQL (Phase 4 AI agents)
- **Mobile**: React Native with Expo (iOS/Android)
- **Phase 4 Intelligence**: Assignment analysis, performance tracking, predictive assistant

## 📋 Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 15+ installed
- [ ] Expo CLI installed (`npm install -g expo-cli`)
- [ ] API keys (OpenAI or Anthropic for AI features)

## 🎯 Development Setup (5 minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL (PostgreSQL connection)
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - OPENAI_API_KEY or ANTHROPIC_API_KEY

# Create database
createdb assignment_sync

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend will be running at: http://localhost:8000
API docs at: http://localhost:8000/api/v1/docs

### 2. Mobile App Setup

```bash
# Navigate to mobile app
cd mobile

# Install dependencies
npm install

# Start Expo development server
npm start
```

Then:
- Press `i` for iOS simulator (Mac only)
- Press `a` for Android emulator
- Scan QR code with Expo Go app on physical device

### 3. Test the Connection

1. Open mobile app
2. Register a new account
3. Create an assignment
4. View AI analysis on assignment detail screen
5. Check dashboard for health score

## 🌐 Production Deployment

### Option A: Railway (Easiest - Recommended for MVP)

**Backend:**
1. Push code to GitHub
2. Go to [Railway.app](https://railway.app)
3. "New Project" → "Deploy from GitHub"
4. Select your repo
5. Add PostgreSQL plugin
6. Set environment variables
7. Deploy!

**Cost**: ~$5-20/month

### Option B: Digital Ocean App Platform

**Backend:**
1. Push to GitHub
2. Go to Digital Ocean
3. Create new App
4. Connect GitHub repo
5. Add PostgreSQL database
6. Configure environment variables
7. Deploy

**Cost**: ~$12-25/month

### Option C: AWS (Most Scalable)

**Backend:**
1. Set up AWS account
2. Create RDS PostgreSQL instance
3. Deploy to Elastic Beanstalk or ECS
4. Configure environment variables
5. Set up CloudFront CDN

**Cost**: ~$20-50/month (with free tier)

### Mobile App Deployment

**For Testing (TestFlight/Internal Testing):**
```bash
cd mobile

# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build for iOS
eas build --platform ios --profile preview

# Build for Android
eas build --platform android --profile preview
```

**For Production (App Store/Play Store):**

See full guide in: `/mobile/README.md` and `APP_STORE_DEPLOYMENT_GUIDE.md`

## 🔐 Security Checklist

Before going to production:

- [ ] Change SECRET_KEY in .env
- [ ] Use strong database password
- [ ] Enable HTTPS (Railway/DO do this automatically)
- [ ] Set up CORS properly (limit allowed origins)
- [ ] Enable rate limiting
- [ ] Review API authentication
- [ ] Store API keys securely (never commit to git)
- [ ] Set up database backups
- [ ] Configure monitoring (Sentry, LogRocket)

## 📊 Monitoring Setup

### Backend Monitoring

```bash
# Add to requirements.txt
pip install sentry-sdk[fastapi]
```

```python
# In app/main.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Mobile Monitoring

```bash
cd mobile
npm install @sentry/react-native
```

## 🧪 Testing Before Launch

### Backend Tests
```bash
cd backend
pytest
```

### Mobile Tests
```bash
cd mobile
npm test
```

### Integration Test Checklist
- [ ] User can register
- [ ] User can login
- [ ] User can create assignment
- [ ] AI analysis works
- [ ] Health score displays
- [ ] Risk assessment works
- [ ] Predictions generate
- [ ] Analytics load

## 📈 Scaling Considerations

### When to Scale

**Signs you need to scale:**
- Response times > 500ms
- Database connections maxed out
- Server CPU > 80%
- 1000+ active users

**Scaling strategies:**
1. Add Redis cache
2. Increase database connection pool
3. Use background workers (Celery)
4. Add load balancer
5. Use CDN for static assets

## 💰 Cost Estimates

### MVP (0-100 users)
- Backend hosting: $5-15/month (Railway)
- Database: Included
- AI API calls: ~$10-50/month
- **Total**: $15-65/month

### Small Scale (100-1000 users)
- Backend hosting: $25-50/month
- Database: $15-25/month
- AI API calls: ~$100-200/month
- Monitoring: $10-20/month
- **Total**: $150-295/month

### Medium Scale (1000-10000 users)
- Backend hosting: $100-200/month
- Database: $50-100/month
- AI API calls: ~$500-1000/month
- CDN: $20-50/month
- Monitoring: $50-100/month
- **Total**: $720-1450/month

## 🎓 Phase 4 AI Features

Your app now includes these Phase 4 agents:

1. **Assignment Intelligence** (`/api/v1/intelligence`)
   - Bloom's Taxonomy analysis
   - Complexity scoring
   - Resource recommendations
   - Skill identification

2. **Performance Analytics** (`/api/v1/analytics`)
   - Academic health scoring
   - Time series tracking
   - Trend detection
   - Productivity patterns

3. **Predictive Assistant** (`/api/v1/predictions`)
   - Risk assessment
   - Deadline predictions
   - Workload optimization
   - Proactive suggestions

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check database connection
psql -h localhost -U user -d assignment_sync

# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Mobile app won't connect to API
- Check `src/services/api.ts` has correct URL
- If using physical device, use your computer's IP (not localhost)
- Ensure backend is running

### Database migrations fail
```bash
# Reset migrations (CAUTION: deletes data)
alembic downgrade base
alembic upgrade head

# Or create new migration
alembic revision --autogenerate -m "fix"
alembic upgrade head
```

## 📚 Next Steps

1. **Week 1-2**: Test locally, fix bugs
2. **Week 3-4**: Deploy to staging (Railway)
3. **Week 5-6**: Beta testing with 10-20 users
4. **Week 7-8**: Submit to App Store/Play Store review
5. **Week 9-12**: Launch and iterate

## 🆘 Need Help?

- Backend API docs: http://localhost:8000/api/v1/docs
- Backend README: `/backend/README.md`
- Mobile README: `/mobile/README.md`
- Full deployment guide: `APP_STORE_DEPLOYMENT_GUIDE.md`
- Learning resources: `COMPLETE_LEARNING_ROADMAP.md`

## ✅ Launch Checklist

Before launching to real users:

- [ ] All tests passing
- [ ] Backend deployed and accessible
- [ ] Database backups configured
- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] Error tracking set up (Sentry)
- [ ] Analytics set up (optional)
- [ ] Terms of Service written
- [ ] Privacy Policy written
- [ ] Support email set up
- [ ] App Store listing prepared
- [ ] Screenshots and promotional materials ready
- [ ] Beta testing completed
- [ ] Performance tested (load testing)
- [ ] Security audit completed

## 🎉 You're Ready!

Your Assignment Calendar Sync app is now ready for deployment. Start with Railway for the backend, test thoroughly with TestFlight/Internal Testing, then submit to app stores.

Good luck! 🚀
