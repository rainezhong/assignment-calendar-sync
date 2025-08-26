# Assignment Calendar Sync Tool

A comprehensive Python-based tool for automatically synchronizing educational assignments from various learning management systems to Google Calendar.

## Overview

This tool helps students and educators stay organized by automatically scraping assignment information from educational platforms and syncing them to Google Calendar. It provides automated scheduling, deadline tracking, and intelligent reminders for academic tasks.

## Features

- **Multi-Platform Support**: Scrape assignments from various educational platforms
- **Google Calendar Integration**: Seamless synchronization with Google Calendar
- **Smart Scheduling**: Intelligent deadline detection and reminder creation
- **Data Persistence**: Local database storage for offline access and historical tracking
- **Configurable Automation**: Scheduled sync operations with customizable intervals
- **Extensible Architecture**: Modular design for easy platform additions

## Project Structure

```
assignment-calendar-sync/
├── src/
│   ├── scraping/           # Web scraping modules for different platforms
│   ├── data_processing/    # Data parsing and transformation utilities
│   ├── calendar_integration/ # Google Calendar API integration
│   └── utilities/          # Helper functions and common utilities
├── config/                 # Configuration files and settings
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
└── main.py                # Main entry point
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account (for Calendar API)
- Chrome/Firefox browser (for Selenium)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/assignment-calendar-sync.git
cd assignment-calendar-sync
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Configure Google Calendar API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Create credentials (OAuth 2.0 Client ID)
   - Download credentials as `credentials.json` to `config/`

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Google Calendar API
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
CALENDAR_ID=primary

# Database
DATABASE_URL=sqlite:///assignments.db

# Scraping Configuration
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30

# Scheduling
SYNC_INTERVAL_HOURS=6
REMINDER_MINUTES=1440  # 24 hours before deadline

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/sync.log
```

### Platform Configuration

Edit `config/platforms.yaml` to add educational platforms:

```yaml
platforms:
  - name: "Canvas"
    url: "https://canvas.yourschool.edu"
    scraper: "canvas_scraper"
    credentials_required: true
    
  - name: "Blackboard"
    url: "https://blackboard.yourschool.edu"
    scraper: "blackboard_scraper"
    credentials_required: true
```

## Usage

### Command Line Interface

```bash
# Run a one-time sync
python main.py sync

# Start the scheduler daemon
python main.py schedule

# Add a new platform
python main.py add-platform --name "Moodle" --url "https://moodle.school.edu"

# View upcoming assignments
python main.py list --days 7

# Clear local cache
python main.py clear-cache
```

### Python API

```python
from src.scraping import UniversalScraper
from src.calendar_integration import GoogleCalendarSync
from src.data_processing import AssignmentProcessor

# Initialize components
scraper = UniversalScraper(config_path="config/platforms.yaml")
processor = AssignmentProcessor()
calendar = GoogleCalendarSync()

# Scrape assignments
raw_assignments = scraper.scrape_all_platforms()

# Process and normalize data
assignments = processor.process(raw_assignments)

# Sync to Google Calendar
calendar.sync_assignments(assignments)
```

## Module Documentation

### Scraping Module

Handles web scraping from various educational platforms:

- `base_scraper.py`: Abstract base class for platform scrapers
- `canvas_scraper.py`: Canvas LMS scraper implementation
- `blackboard_scraper.py`: Blackboard scraper implementation
- `universal_scraper.py`: Factory pattern for managing multiple scrapers

### Data Processing Module

Processes and normalizes assignment data:

- `parser.py`: Parse raw HTML/JSON data
- `normalizer.py`: Standardize data format across platforms
- `validator.py`: Validate assignment data integrity
- `filters.py`: Filter assignments based on criteria

### Calendar Integration Module

Manages Google Calendar synchronization:

- `auth.py`: OAuth2 authentication handler
- `calendar_client.py`: Google Calendar API wrapper
- `sync_manager.py`: Synchronization logic and conflict resolution
- `event_builder.py`: Create calendar events from assignments

### Utilities Module

Common utilities and helpers:

- `logger.py`: Logging configuration and utilities
- `database.py`: Database models and operations
- `config.py`: Configuration management
- `scheduler.py`: Task scheduling utilities

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test module
pytest tests/test_scraping.py

# Run integration tests only
pytest tests/integration/
```

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-platform`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit with descriptive messages
6. Push to your fork
7. Submit a pull request

## Troubleshooting

### Common Issues

1. **Selenium WebDriver Issues**
   - Ensure ChromeDriver/GeckoDriver is installed and in PATH
   - Update driver version to match browser version

2. **Google Calendar API Errors**
   - Verify API is enabled in Google Cloud Console
   - Check OAuth2 credentials are valid
   - Ensure calendar permissions are granted

3. **Scraping Failures**
   - Check if platform structure has changed
   - Verify login credentials are correct
   - Increase timeout values in configuration

## Security Considerations

- Never commit credentials or `.env` files
- Use environment variables for sensitive data
- Implement rate limiting to avoid being blocked
- Store passwords encrypted if persistence is required
- Regular security audits of dependencies

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Google Calendar API documentation
- Selenium WebDriver community
- Educational platform developers

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: https://docs.example.com

## Roadmap

- [ ] Add support for more educational platforms
- [ ] Implement mobile app notifications
- [ ] Add iCal export functionality
- [ ] Create web interface for configuration
- [ ] Add machine learning for smart scheduling
- [ ] Implement team/group assignment sharing
- [ ] Add support for recurring assignments
- [ ] Create browser extension for quick adding