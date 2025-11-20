# Next.js Web App - Complete Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Create Next.js App

```bash
# Create Next.js app with TypeScript, Tailwind, and App Router
npx create-next-app@latest web \
  --typescript \
  --tailwind \
  --app \
  --import-alias "@/*" \
  --no-src-dir

cd web
```

**During setup, answer:**
- ✅ TypeScript? Yes
- ✅ ESLint? Yes
- ✅ Tailwind CSS? Yes
- ✅ `src/` directory? No
- ✅ App Router? Yes
- ✅ Import alias? Yes (@/*)

### Step 2: Install Additional Dependencies

```bash
npm install axios react-query
npm install @tanstack/react-query
npm install react-hook-form
npm install lucide-react  # Icons
```

### Step 3: Create Environment Files

```bash
# Development
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF

# Production (create later)
cat > .env.production << 'EOF'
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app/api/v1
EOF
```

### Step 4: Copy All Component Files

I'll provide all the files below. Copy them into your `web/` directory following the structure.

---

## 📁 Project Structure

```
web/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing/redirect
│   ├── login/
│   │   └── page.tsx            # Login page
│   ├── signup/
│   │   └── page.tsx            # Signup page
│   ├── dashboard/
│   │   └── page.tsx            # Main dashboard
│   ├── ready/
│   │   └── page.tsx            # Ready to submit
│   └── profile/
│       └── page.tsx            # User profile
├── components/
│   ├── Navbar.tsx              # Navigation bar
│   ├── ProtectedRoute.tsx      # Auth wrapper
│   ├── JobCard.tsx             # Job display card
│   └── ApplicationCard.tsx     # Application card
├── lib/
│   ├── api.ts                  # API client
│   ├── auth.ts                 # Auth helpers
│   └── types.ts                # TypeScript types
├── contexts/
│   └── AuthContext.tsx         # Auth state management
├── .env.local                  # Environment variables
└── package.json
```

---

## 🔧 File Contents

I'll create each file for you now. After this message, you'll have:
1. Complete API client
2. All pages (login, dashboard, ready, profile)
3. All components
4. Auth context
5. Types

---

## ⏭️ Next Steps After Files Are Created

1. **Copy all files** into your `web/` directory
2. **Update .env.local** with your backend URL
3. **Test locally:**
   ```bash
   npm run dev
   # Opens at http://localhost:3000
   ```
4. **Deploy to Vercel:**
   ```bash
   npm i -g vercel
   vercel
   ```

---

## 📦 What You'll Get

### Pages:
- **Landing (/)** - Redirects to dashboard or login
- **Login (/login)** - Email/password login
- **Signup (/signup)** - New user registration
- **Dashboard (/dashboard)** - Main app with stats and ready alert
- **Ready to Submit (/ready)** - Queue of prepared applications
- **Profile (/profile)** - Resume upload, preferences, settings

### Features:
- ✅ JWT authentication with context
- ✅ Protected routes (auto-redirect if not logged in)
- ✅ Responsive design (works on mobile)
- ✅ Tailwind CSS styling
- ✅ React Query for data fetching
- ✅ Type-safe API client
- ✅ Loading states
- ✅ Error handling

---

## 🎨 How It Looks

### Desktop Dashboard:
- Clean, modern design
- Stats cards (applications, interviews, offers)
- Prominent "Ready to Submit" alert
- Job matches list
- Navigation bar

### Mobile:
- Fully responsive
- Stack layout on small screens
- Touch-friendly buttons
- Works in any mobile browser

---

## 🚀 Deployment

### Vercel (Recommended - FREE!)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd web
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name? college-assistant
# - Directory? ./
# - Want to override settings? No

# Set environment variable in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app/api/v1
```

**Result:** `https://college-assistant.vercel.app`

### Alternative: Railway

```bash
# In your Railway project, add new service
# Connect to GitHub
# Set root directory: "web"
# Set build command: npm run build
# Set start command: npm start

# Add environment variable:
# NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app/api/v1
```

---

## 🧪 Testing

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend (new terminal)
cd web
npm run dev

# Open http://localhost:3000
# Test:
# 1. Sign up new user
# 2. Login
# 3. Upload resume
# 4. Set preferences
# 5. Check dashboard
```

---

## 💰 Costs

- **Vercel:** FREE (generous free tier)
- **Backend (Railway):** $20-30/month
- **OpenAI:** $5-15/month
- **Total:** $25-45/month

Split among 5 friends = **$5-9 per person**

---

Ready for the files? I'll create them all in the next messages!
