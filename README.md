# Assignment Calendar Sync

A Python application that syncs assignments from Gradescope (via web scraping) to Google Calendar, with support for school SSO authentication.

## Features

- **Gradescope Scraping**: Supports both direct login and SSO (School Credentials)
- **Session Persistence**: Saves login sessions to avoid repeated authentication
- **Google Calendar Sync**: Creates events with smart duplicate detection
- **Configurable Settings**: Reminder times, sync window, and more
- **Dry-run Mode**: Preview changes before syncing

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
- Gradescope credentials OR enable SSO mode
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

## Authentication Setup

### Gradescope Options

#### Option 1: SSO (School Credentials)
Set in `.env`:
```
GRADESCOPE_USE_SSO=true
```
You'll be prompted to complete login in your browser.

#### Option 2: Direct Login
Set in `.env`:
```
GRADESCOPE_EMAIL=your_email@school.edu
GRADESCOPE_PASSWORD=your_password
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
- `combined_scraper.py` - Gradescope scraper wrapper
- `scraper.py` - Gradescope web scraper with SSO support
- `calendar_integration.py` - Google Calendar API integration
- `config.py` - Configuration management
- `.env` - Environment variables (create from .env.example)
- `requirements.txt` - Python dependencies

## How It Works

1. **Gradescope**: Uses Selenium with SSO support or direct login
2. **Session Management**: Saves cookies for faster subsequent runs
3. **Calendar Sync**: Creates events with smart duplicate detection
4. **Filtering**: Only syncs assignments within configured time window

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