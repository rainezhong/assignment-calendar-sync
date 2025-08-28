# Assignment Calendar Sync - Desktop App

A beautiful, cross-platform desktop application that automatically syncs assignments from Gradescope to Google Calendar.

## 🚀 Quick Start

### For End Users (Download & Install)

1. **Download** the latest release for your platform:
   - **macOS**: `Assignment-Calendar-Sync-1.0.0.dmg`
   - **Windows**: `Assignment-Calendar-Sync-1.0.0.exe`  
   - **Linux**: `Assignment-Calendar-Sync-1.0.0.AppImage`

2. **Install** the app like any other desktop application

3. **Configure** your settings:
   - Add your Gradescope email and password
   - Set up Google Calendar API credentials
   - Choose your sync preferences

4. **Sync** your assignments with one click!

## 🛠️ For Developers (Build from Source)

### Prerequisites

- **Node.js 16+** (with npm)
- **Python 3.7+** (with pip)
- **Git**

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd assignment-calendar-sync
```

2. **Run the build script:**
```bash
node scripts/build.js
```

Or manually:

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
cd python && pip3 install -r requirements.txt && cd ..

# Run in development mode
npm run electron-dev

# Build for production
npm run build
```

### Development Commands

```bash
# Development mode (with DevTools)
npm run electron-dev

# Production mode
npm run electron

# Build for current platform
npm run build

# Build for specific platforms
npm run build:mac
npm run build:win
npm run build:linux

# Build for all platforms
npm run build:all

# Package without installer (for testing)
npm run pack
```

## 📋 Features

### ✅ What's Included

- **🎨 Beautiful UI** - Modern, responsive interface
- **🔐 Secure Storage** - Settings saved locally and encrypted
- **🔄 Real-time Sync** - Live progress updates during sync
- **📱 Cross-platform** - Works on macOS, Windows, and Linux
- **⚙️ Easy Configuration** - Simple forms for all settings
- **🧪 Test Functions** - Verify settings before syncing
- **📊 Progress Tracking** - Visual feedback and logs
- **🔍 Dry Run Mode** - Preview changes before applying
- **📅 Smart Scheduling** - Flexible date range options
- **⚡ Quick Settings** - One-click common configurations

### 🎯 Core Functionality

1. **Scrapes Gradescope** - Automatically logs in and extracts assignments
2. **Parses Dates** - Handles various date formats intelligently  
3. **Creates Events** - Adds assignments to Google Calendar with reminders
4. **Avoids Duplicates** - Smart detection prevents duplicate events
5. **Error Handling** - Comprehensive error recovery and reporting

## 🖥️ App Screens

### Dashboard
- Quick sync buttons (Sync Now / Dry Run)
- Recent activity log
- Sync statistics and status
- Quick settings panel

### Settings
- **Gradescope Login** - Email and password with test button
- **Google Calendar** - API credentials and calendar selection
- **Sync Options** - Days ahead, reminders, timezone
- **Test Configuration** - Validate entire setup

### Progress Modal
- Real-time sync progress with percentage
- Live log output from Python processes
- Cancel button for long-running operations
- Auto-close on successful completion

## 🔧 Configuration

### Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials (Desktop application)
5. Copy Client ID and Client Secret to app settings

### Gradescope Setup

Simply enter your Gradescope email and password. The app stores them securely and uses them only for scraping assignments.

## 📁 Project Structure

```
assignment-calendar-sync/
├── electron/              # Electron main process
│   └── main.js            # App entry point & IPC handlers
├── renderer/              # Frontend (HTML/CSS/JS)
│   ├── index.html         # Main UI
│   ├── style.css          # Styling
│   └── app.js             # Frontend logic
├── python/                # Python backend (unchanged)
│   ├── main.py            # Main script
│   ├── scraper.py         # Gradescope scraper
│   ├── calendar_integration.py
│   └── ... (all existing Python files)
├── scripts/               # Build scripts
│   └── build.js           # Automated build process
├── build/                 # Build assets (icons, etc.)
├── dist/                  # Built applications
└── package.json           # Electron app config
```

## 🔄 How It Works

### Frontend → Backend Communication

1. **Frontend (Electron Renderer)** - User interacts with HTML/CSS/JS interface
2. **IPC Bridge** - Electron's Inter-Process Communication handles requests
3. **Main Process** - Spawns Python processes and manages communication
4. **Python Backend** - Your existing scraping and calendar logic (unchanged!)
5. **Results** - Stream back to frontend in real-time

### Python Integration

The app preserves your existing Python codebase 100%. It simply:

- Creates `.env` files from GUI settings
- Spawns `python3 main.py` with appropriate arguments  
- Streams stdout/stderr back to the UI
- Handles process lifecycle (start/stop/cleanup)

## 🚢 Building & Distribution

### Automated Build

```bash
# Build for all platforms
node scripts/build.js all

# Build for specific platform
node scripts/build.js mac    # or win, linux
```

### Manual Build Steps

1. **Prepare**: Install dependencies and create assets
2. **Bundle**: Package Python code with Electron app
3. **Build**: Create platform-specific installers
4. **Test**: Verify app works on target platform
5. **Distribute**: Upload installers to release channels

### Output Files

- **macOS**: `.dmg` installer with drag-to-Applications
- **Windows**: `.exe` NSIS installer with uninstaller
- **Linux**: `.AppImage` portable executable

## 🐛 Troubleshooting

### Common Issues

**"Python not found"**
- Install Python 3.7+ and ensure it's in PATH
- Try running `python3 --version` in terminal

**"Chrome driver not found"**  
- Install ChromeDriver: `brew install chromedriver` (Mac)
- Or download from https://chromedriver.chromium.org/

**"Build failed"**
- Run `npm install` to install dependencies
- Check Node.js version (16+ required)
- Verify all required files exist

**"Authentication failed"**
- Check Google API credentials are correct
- Verify Gradescope login works manually
- Delete `python/token.json` and re-authenticate

### Debug Mode

Enable detailed logging:
1. Check "Enable debug mode" in Settings
2. Or run with: `DEBUG=1 npm run electron-dev`

### Log Files

Check `python/logs/sync.log` for detailed Python execution logs.

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Check existing discussions
- **Feature Requests**: Use GitHub Issues with enhancement label

---

**Ready to sync your assignments?** Download the latest release or build from source and never miss a deadline again! 🎓✨