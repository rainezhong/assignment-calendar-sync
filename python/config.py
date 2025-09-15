"""
Simple configuration system with validation and helpful error messages
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigError(Exception):
    """Configuration validation error"""
    pass


class Config:
    """Simple configuration manager with validation"""
    
    def __init__(self):
        """Initialize and validate configuration"""
        self.errors = []
        self.warnings = []
        
        # Load and validate all settings
        self._load_google_calendar_settings()
        self._load_gradescope_settings()
        self._load_canvas_settings()
        self._load_notion_settings()
        self._load_app_settings()
        
        # Check for critical errors
        if self.errors:
            self._print_config_errors()
            sys.exit(1)
        
        # Show warnings if any
        if self.warnings:
            self._print_config_warnings()
    
    def _load_google_calendar_settings(self):
        """Load Google Calendar API settings (OPTIONAL - only for direct calendar integration)"""
        # Optional settings - only needed if user wants direct Google Calendar integration
        self.GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '').strip()
        self.GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
        
        # Optional settings with defaults
        self.GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary').strip()
        
        # File paths for Google OAuth
        self.TOKEN_FILE = os.getenv('TOKEN_FILE', 'token.json')
        self.CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
        
        # Google Calendar API is OPTIONAL - we use ICS file generation instead
        # Only validate if user has provided partial Google credentials
        if self.GOOGLE_CLIENT_ID and not self.GOOGLE_CLIENT_SECRET:
            self.warnings.append(
                "GOOGLE_CLIENT_ID is set but GOOGLE_CLIENT_SECRET is missing. "
                "Google Calendar integration won't work without both. "
                "Leave both empty to use ICS file generation instead."
            )
        
        if self.GOOGLE_CLIENT_SECRET and not self.GOOGLE_CLIENT_ID:
            self.warnings.append(
                "GOOGLE_CLIENT_SECRET is set but GOOGLE_CLIENT_ID is missing. "
                "Google Calendar integration won't work without both. "
                "Leave both empty to use ICS file generation instead."
            )
        
        # Validate calendar ID format (basic check)
        if self.GOOGLE_CALENDAR_ID and '@' in self.GOOGLE_CALENDAR_ID:
            if not (self.GOOGLE_CALENDAR_ID.endswith('@group.calendar.google.com') or 
                    '@' in self.GOOGLE_CALENDAR_ID):
                self.warnings.append(
                    f"GOOGLE_CALENDAR_ID '{self.GOOGLE_CALENDAR_ID}' might be invalid. "
                    "Use 'primary' for your main calendar or a valid calendar ID."
                )
    
    def _load_notion_settings(self):
        """Load Notion API settings (OPTIONAL - for direct Notion Calendar sync)"""
        # Optional settings - only needed if user wants direct Notion integration
        self.NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN', '').strip()
        self.NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', '').strip()
        
        # Notion integration is optional - validate only if provided
        if self.NOTION_API_TOKEN and not self.NOTION_DATABASE_ID:
            self.warnings.append(
                "NOTION_API_TOKEN is set but NOTION_DATABASE_ID is missing. "
                "Notion Calendar integration won't work without both."
            )
        
        if self.NOTION_DATABASE_ID and not self.NOTION_API_TOKEN:
            self.warnings.append(
                "NOTION_DATABASE_ID is set but NOTION_API_TOKEN is missing. "
                "Notion Calendar integration won't work without both."
            )
        
        # Validate database ID format (basic check)
        if self.NOTION_DATABASE_ID and len(self.NOTION_DATABASE_ID) != 32:
            self.warnings.append(
                f"NOTION_DATABASE_ID '{self.NOTION_DATABASE_ID}' doesn't look like a valid database ID. "
                "It should be a 32-character UUID without dashes."
            )
    
    def _load_gradescope_settings(self):
        """Load Gradescope settings"""
        self.GRADESCOPE_EMAIL = os.getenv('GRADESCOPE_EMAIL', '').strip()
        self.GRADESCOPE_PASSWORD = os.getenv('GRADESCOPE_PASSWORD', '').strip()
        self.GRADESCOPE_USE_SSO = os.getenv('GRADESCOPE_USE_SSO', 'false').lower() in ('true', '1', 'yes', 'on')
        
        # Validation - SSO or direct credentials required
        if self.GRADESCOPE_USE_SSO:
            # SSO mode - no credentials needed
            pass
        else:
            # Direct login mode - need email and password
            if not self.GRADESCOPE_EMAIL:
                self.errors.append(
                    "GRADESCOPE_EMAIL is missing. "
                    "Please add your Gradescope email to the .env file, "
                    "or set GRADESCOPE_USE_SSO=true for SSO login."
                )
            elif '@' not in self.GRADESCOPE_EMAIL:
                self.errors.append(
                    f"GRADESCOPE_EMAIL '{self.GRADESCOPE_EMAIL}' doesn't look like a valid email address."
                )
            
            if not self.GRADESCOPE_PASSWORD:
                self.errors.append(
                    "GRADESCOPE_PASSWORD is missing. "
                    "Please add your Gradescope password to the .env file, "
                    "or set GRADESCOPE_USE_SSO=true for SSO login."
                )
    
    def _load_canvas_settings(self):
        """Load optional Canvas settings"""
        self.CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN', '').strip()
        self.CANVAS_API_URL = os.getenv('CANVAS_API_URL', '').strip()
        
        # Canvas is optional, so only validate if provided
        if self.CANVAS_API_TOKEN and not self.CANVAS_API_URL:
            self.warnings.append(
                "CANVAS_API_TOKEN is set but CANVAS_API_URL is missing. "
                "Canvas integration won't work without both."
            )
        
        if self.CANVAS_API_URL and not self.CANVAS_API_TOKEN:
            self.warnings.append(
                "CANVAS_API_URL is set but CANVAS_API_TOKEN is missing. "
                "Canvas integration won't work without both."
            )
        
        # Validate URL format
        if self.CANVAS_API_URL:
            if not (self.CANVAS_API_URL.startswith('http://') or 
                    self.CANVAS_API_URL.startswith('https://')):
                self.warnings.append(
                    f"CANVAS_API_URL should start with http:// or https://"
                )
    
    def _load_app_settings(self):
        """Load application settings with validation"""
        # Browser settings
        headless_str = os.getenv('HEADLESS_BROWSER', 'true').lower()
        self.HEADLESS_BROWSER = headless_str in ('true', '1', 'yes', 'on')
        
        # Validate and parse SYNC_DAYS_AHEAD
        sync_days_str = os.getenv('SYNC_DAYS_AHEAD', '30')
        try:
            self.SYNC_DAYS_AHEAD = int(sync_days_str)
            if self.SYNC_DAYS_AHEAD < 1:
                self.warnings.append(
                    f"SYNC_DAYS_AHEAD ({self.SYNC_DAYS_AHEAD}) is less than 1. Using default of 30."
                )
                self.SYNC_DAYS_AHEAD = 30
            elif self.SYNC_DAYS_AHEAD > 365:
                self.warnings.append(
                    f"SYNC_DAYS_AHEAD ({self.SYNC_DAYS_AHEAD}) is more than 365 days. "
                    "This might create too many calendar events."
                )
        except ValueError:
            self.warnings.append(
                f"SYNC_DAYS_AHEAD '{sync_days_str}' is not a valid number. Using default of 30."
            )
            self.SYNC_DAYS_AHEAD = 30
        
        # Validate and parse DEFAULT_REMINDER_MINUTES
        reminder_str = os.getenv('DEFAULT_REMINDER_MINUTES', '60')
        try:
            self.DEFAULT_REMINDER_MINUTES = int(reminder_str)
            if self.DEFAULT_REMINDER_MINUTES < 0:
                self.warnings.append(
                    f"DEFAULT_REMINDER_MINUTES cannot be negative. Using default of 60."
                )
                self.DEFAULT_REMINDER_MINUTES = 60
            elif self.DEFAULT_REMINDER_MINUTES > 10080:  # More than a week
                self.warnings.append(
                    f"DEFAULT_REMINDER_MINUTES ({self.DEFAULT_REMINDER_MINUTES}) is more than a week. "
                    "That's a very early reminder!"
                )
        except ValueError:
            self.warnings.append(
                f"DEFAULT_REMINDER_MINUTES '{reminder_str}' is not a valid number. Using default of 60."
            )
            self.DEFAULT_REMINDER_MINUTES = 60
        
        # Additional settings
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() in ('true', '1', 'yes', 'on')
        self.DRY_RUN_DEFAULT = os.getenv('DRY_RUN_DEFAULT', 'false').lower() in ('true', '1', 'yes', 'on')
        
        # Timezone setting (optional)
        self.TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')
        
        # Target semester setting
        self.TARGET_SEMESTER = os.getenv('TARGET_SEMESTER', 'current')
        
        # Chrome driver path (optional)
        self.CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '').strip() or None
        
        if self.CHROMEDRIVER_PATH and not os.path.exists(self.CHROMEDRIVER_PATH):
            self.warnings.append(
                f"CHROMEDRIVER_PATH '{self.CHROMEDRIVER_PATH}' doesn't exist. "
                "Will try to use chromedriver from PATH instead."
            )
            self.CHROMEDRIVER_PATH = None
    
    def _print_config_errors(self):
        """Print configuration errors in a friendly format"""
        print("\n" + "=" * 60)
        print("❌ CONFIGURATION ERRORS")
        print("=" * 60)
        
        for i, error in enumerate(self.errors, 1):
            print(f"\n{i}. {error}")
        
        print("\n" + "-" * 60)
        print("Please fix these errors in your .env file and try again.")
        print("Copy .env.example to .env if you haven't already:")
        print("  cp .env.example .env")
        print("=" * 60 + "\n")
    
    def _print_config_warnings(self):
        """Print configuration warnings"""
        print("\n" + "=" * 60)
        print("⚠️  Configuration Warnings")
        print("=" * 60)
        
        for warning in self.warnings:
            print(f"• {warning}")
        
        print("=" * 60 + "\n")
    
    def print_config_summary(self):
        """Print a summary of the current configuration"""
        print("\n" + "=" * 60)
        print("📋 Configuration Summary")
        print("=" * 60)
        
        print("\nGoogle Calendar:")
        print(f"  Client ID: {'✓ Set' if self.GOOGLE_CLIENT_ID else '✗ Missing'}")
        print(f"  Client Secret: {'✓ Set' if self.GOOGLE_CLIENT_SECRET else '✗ Missing'}")
        print(f"  Calendar ID: {self.GOOGLE_CALENDAR_ID}")
        
        print("\nGradescope:")
        if self.GRADESCOPE_USE_SSO:
            print("  Authentication: SSO (School Credentials)")
        else:
            print(f"  Email: {self.GRADESCOPE_EMAIL or 'Not set'}")
            print(f"  Password: {'✓ Set' if self.GRADESCOPE_PASSWORD else '✗ Missing'}")
        
        if self.CANVAS_API_TOKEN:
            print("\nCanvas:")
            print(f"  API URL: {self.CANVAS_API_URL}")
            print(f"  API Token: {'✓ Set' if self.CANVAS_API_TOKEN else '✗ Missing'}")
        
        if self.NOTION_API_TOKEN:
            print("\nNotion Calendar:")
            print(f"  API Token: {'✓ Set' if self.NOTION_API_TOKEN else '✗ Missing'}")
            print(f"  Database ID: {'✓ Set' if self.NOTION_DATABASE_ID else '✗ Missing'}")
        
        print("\nSettings:")
        print(f"  Sync days ahead: {self.SYNC_DAYS_AHEAD}")
        print(f"  Reminder minutes: {self.DEFAULT_REMINDER_MINUTES}")
        print(f"  Headless browser: {self.HEADLESS_BROWSER}")
        print(f"  Debug mode: {self.DEBUG_MODE}")
        print(f"  Timezone: {self.TIMEZONE}")
        
        print("=" * 60 + "\n")
    
    def validate_runtime_requirements(self):
        """Check runtime requirements like Chrome/Chromedriver"""
        import shutil
        
        runtime_errors = []
        
        # Check for Chrome/Chromium
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # Mac
            '/usr/bin/google-chrome',  # Linux
            '/usr/bin/chromium-browser',  # Linux
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Windows
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',  # Windows
        ]
        
        chrome_found = any(os.path.exists(path) for path in chrome_paths)
        if not chrome_found and not shutil.which('google-chrome') and not shutil.which('chromium'):
            runtime_errors.append(
                "Chrome/Chromium browser not found. "
                "Please install Chrome from https://www.google.com/chrome/"
            )
        
        # Check for Chromedriver
        if self.CHROMEDRIVER_PATH:
            if not os.path.exists(self.CHROMEDRIVER_PATH):
                runtime_errors.append(
                    f"Chromedriver not found at {self.CHROMEDRIVER_PATH}"
                )
        elif not shutil.which('chromedriver'):
            runtime_errors.append(
                "Chromedriver not found in PATH. "
                "Install it with:\n"
                "  Mac: brew install chromedriver\n"
                "  Ubuntu: sudo apt-get install chromium-chromedriver\n"
                "  Or download from https://chromedriver.chromium.org/"
            )
        
        if runtime_errors:
            print("\n" + "=" * 60)
            print("❌ RUNTIME REQUIREMENTS MISSING")
            print("=" * 60)
            for error in runtime_errors:
                print(f"\n• {error}")
            print("=" * 60 + "\n")
            return False
        
        return True


# Create a singleton config instance
_config = None

def get_config():
    """Get or create the configuration singleton"""
    global _config
    if _config is None:
        _config = Config()
    return _config


# For backward compatibility, expose config values at module level
# This allows "import config" and "config.SETTING_NAME" to work
if _config is None:
    _config = Config()

# Export all config values as module attributes
for attr in dir(_config):
    if not attr.startswith('_') and attr.isupper():
        globals()[attr] = getattr(_config, attr)


# Convenience function for testing configuration
def test_config():
    """Test configuration and print summary"""
    config = get_config()
    config.print_config_summary()
    
    # Check runtime requirements
    if config.validate_runtime_requirements():
        print("✅ All runtime requirements met!\n")
    else:
        print("❌ Some runtime requirements are missing.\n")
        return False
    
    return len(config.errors) == 0


if __name__ == '__main__':
    # If run directly, test the configuration
    if test_config():
        print("Configuration is valid and ready to use!")
    else:
        sys.exit(1)