# Assignment Calendar Sync - Minimal Version

A simple Python script that syncs assignments from Gradescope to Google Calendar.

## Features

- Scrapes assignments from Gradescope using Selenium
- Creates Google Calendar events for assignments with due dates
- Avoids duplicate events
- Configurable reminder times
- Dry-run mode for testing

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials as JSON

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your information:
- Google Calendar API credentials
- Gradescope email and password
- Other optional settings

### 4. Install ChromeDriver

For Selenium to work, you need ChromeDriver:

```bash
# Mac
brew install chromedriver

# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Or download manually from https://chromedriver.chromium.org/
```

## Usage

### Basic Sync

```bash
python main.py
```

### Dry Run (Preview what would be synced)

```bash
python main.py --dry-run
```

### Sync More Days Ahead

```bash
python main.py --days 60  # Sync assignments due in next 60 days
```

### Sync All Assignments

```bash
python main.py --all
```

## File Structure

- `main.py` - Main entry point and sync logic
- `scraper.py` - Gradescope web scraper using Selenium
- `calendar_integration.py` - Google Calendar API integration
- `config.py` - Configuration management
- `.env` - Environment variables (create from .env.example)
- `requirements.txt` - Python dependencies

## How It Works

1. Logs into Gradescope using Selenium
2. Scrapes all courses and their assignments
3. Filters assignments by due date (default: next 30 days)
4. Checks Google Calendar for existing events to avoid duplicates
5. Creates calendar events for new assignments

## Troubleshooting

### ChromeDriver Issues
- Make sure ChromeDriver is installed and in PATH
- Update ChromeDriver if Chrome browser was recently updated

### Google Calendar Authentication
- On first run, a browser window will open for OAuth authentication
- Grant calendar permissions when prompted
- Token is saved to `token.json` for future runs

### Gradescope Login Issues
- Check credentials in `.env` file
- Try setting `HEADLESS_BROWSER=false` to see what's happening

## Notes

- Events are created 1 hour before the due date
- Default reminder is 60 minutes before the event
- Only assignments with due dates are synced
- Duplicate events are automatically skipped

## License

MIT