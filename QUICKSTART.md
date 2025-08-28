# 🚀 Quick Start - Desktop App

## ⚡ Instant Setup (3 Steps)

### 1. **Start the App**
```bash
./start-app.sh
```

### 2. **Configure Settings**  
When the app opens:
- Click **"Settings"** tab
- Enter your **Gradescope email/password**
- Add **Google Calendar API credentials** ([Get them here](https://console.cloud.google.com/))
- Click **"Save Settings"**

### 3. **Sync Your Assignments**
- Go back to **"Dashboard"** 
- Click **"Sync Now"** or **"Dry Run"** (preview mode)
- Watch the magic happen! ✨

---

## 🎯 What You Get

**Desktop App Features:**
- ✅ **Beautiful GUI** - No more command line!
- ✅ **Real-time Progress** - See what's happening live
- ✅ **Settings Management** - Easy configuration forms
- ✅ **Test Functions** - Verify setup before syncing
- ✅ **Activity Log** - Track what happened when
- ✅ **Dry Run Mode** - Preview changes safely

**Same Powerful Backend:**
- ✅ **Smart Scraping** - Handles Gradescope login & extraction
- ✅ **Date Parsing** - Understands various date formats  
- ✅ **Calendar Integration** - Creates events with reminders
- ✅ **Duplicate Detection** - Won't create the same event twice
- ✅ **Error Recovery** - Robust error handling & retry logic

---

## 🔧 Development Mode

For developers or advanced users:

```bash
# Start with DevTools open
./start-app.sh dev

# Or manually
npm run electron-dev
```

---

## 📦 Building Installers

Create downloadable installers for distribution:

```bash
# Build for your current platform
node scripts/build.js

# Build for all platforms  
node scripts/build.js all

# Build for specific platforms
node scripts/build.js mac    # .dmg
node scripts/build.js win    # .exe
node scripts/build.js linux  # .AppImage
```

Built apps will be in the `dist/` folder.

---

## 🆘 Need Help?

**Common Issues:**
- **"Python not found"** → Install Python 3.7+ from [python.org](https://python.org)
- **"npm not found"** → Install Node.js from [nodejs.org](https://nodejs.org)  
- **"Chrome driver error"** → Install Chrome browser
- **"Login failed"** → Check Gradescope credentials in Settings

**Still Stuck?**
1. Check the **Activity Log** in the Dashboard tab
2. Enable **Debug Mode** in Settings for detailed logs
3. Look at `python/logs/sync.log` for Python errors
4. Try **"Test Configuration"** in Settings to diagnose issues

---

## 🎉 That's It!

Your command-line tool is now a beautiful desktop app that anyone can use. The same powerful Python backend, wrapped in a user-friendly interface.

**Happy syncing!** 📚✨