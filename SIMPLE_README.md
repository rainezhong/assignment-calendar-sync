# Assignment Calendar Sync 📚

**Get all your Canvas and Gradescope assignments into your calendar in 2 minutes!**

No complicated API setup required - just run and import the calendar file.

## Quick Start (2 minutes)

### 1. Install Requirements
```bash
pip install selenium requests python-dotenv pytz python-dateutil
```

### 2. Run Setup
```bash
python setup.py
```
This will ask you a few simple questions:
- How you log into Gradescope (school login or email/password)
- Your Canvas token (optional)
- Your timezone

### 3. Sync Your Assignments
```bash
python python/simple_sync.py
```

### 4. Import to Your Calendar
The app creates an `.ics` file that you can:
- **Double-click** to open in your default calendar
- **Drag into** Google Calendar, Outlook, or Apple Calendar
- **Import via** Calendar settings → Import

That's it! 🎉

## What It Does

1. **Fetches assignments** from Canvas (via API) and Gradescope (via browser)
2. **Creates a calendar file** with all your upcoming assignments
3. **You import it** into any calendar app you like

## Features

✅ **No Google API needed** - Just creates a standard calendar file  
✅ **Works with SSO** - Handles school login pages  
✅ **Smart deduplication** - Won't create duplicate events  
✅ **Reminder alerts** - Get notified before assignments are due  

## Troubleshooting

**"Chrome not found"**
- Install Chrome or Chromium browser

**"Can't login to Gradescope"**
- If using SSO, you'll see a browser window - complete the login there
- The app saves your session for next time

**"Canvas not working"**
- Canvas is optional - the app works with just Gradescope
- To add Canvas: Log into Canvas → Settings → New Access Token

## Run It Regularly

Set up a weekly reminder to run:
```bash
python python/simple_sync.py
```

Each time it creates a fresh calendar file with your latest assignments.

## Need Help?

The app is designed to be self-explanatory. If you get stuck:
1. Delete `.env` and run `python setup.py` again
2. Check that Chrome/Chromium is installed
3. Try the `--debug` flag: `python python/simple_sync.py --debug`

---

Made for students who just want their assignments in their calendar without the hassle! 🎓