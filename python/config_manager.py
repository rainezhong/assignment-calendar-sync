#!/usr/bin/env python3
"""
Simplified Configuration Manager
Replaces complex .env setup with user-friendly YAML configuration
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for Academic Assistant"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.defaults = self._load_defaults()

    def _load_defaults(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            "user": {
                "email": "",
                "university": ""
            },
            "gradescope": {
                "method": "sso",
                "username": "",
                "password": ""
            },
            "calendars": {
                "ics": {
                    "enabled": True,
                    "filename": "assignments.ics"
                },
                "google": {
                    "enabled": False,
                    "calendar_id": "primary"
                },
                "notion": {
                    "enabled": False,
                    "token": "",
                    "database_id": ""
                }
            },
            "sync": {
                "frequency": "daily",
                "time_window": 30,
                "auto_start": True
            },
            "courses": {
                "auto_detect": True,
                "include_only": [],
                "exclude": []
            },
            "advanced": {
                "dry_run": False,
                "debug_mode": False,
                "browser_headless": True,
                "retry_attempts": 3
            }
        }

    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            logger.info(f"Config file {self.config_path} not found, creating with defaults")
            self.save_defaults()

        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}

            # Merge with defaults for missing keys
            self.config = self._merge_with_defaults(self.config)

            return self.config

        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            logger.info("Using default configuration")
            self.config = self.defaults.copy()
            return self.config

    def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file"""
        if config:
            self.config = config

        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")

        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def save_defaults(self) -> None:
        """Save default configuration"""
        self.config = self.defaults.copy()
        self.save()

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge config with defaults"""
        def merge_dicts(default: Dict, user: Dict) -> Dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result

        return merge_dicts(self.defaults, config)

    def get(self, key_path: str, default=None) -> Any:
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration and return issues"""
        issues = []

        # Check required fields
        if not self.get('user.email'):
            issues.append("User email is required")

        if self.get('gradescope.method') == 'direct':
            if not self.get('gradescope.username'):
                issues.append("Gradescope username required for direct login")
            if not self.get('gradescope.password'):
                issues.append("Gradescope password required for direct login")

        # Check Google Calendar config
        if self.get('calendars.google.enabled'):
            # Google Calendar validation will be done during auth
            pass

        # Check Notion config
        if self.get('calendars.notion.enabled'):
            if not self.get('calendars.notion.token'):
                issues.append("Notion token required when Notion is enabled")
            if not self.get('calendars.notion.database_id'):
                issues.append("Notion database ID required when Notion is enabled")

        # Check sync settings
        time_window = self.get('sync.time_window')
        if not isinstance(time_window, int) or time_window < 1 or time_window > 365:
            issues.append("Sync time window must be between 1 and 365 days")

        return len(issues) == 0, issues

    def to_legacy_env(self) -> Dict[str, str]:
        """Convert config to legacy .env format for backward compatibility"""
        env_vars = {}

        # User settings
        if self.get('user.email'):
            env_vars['USER_EMAIL'] = self.get('user.email')

        # Gradescope settings
        if self.get('gradescope.method') == 'sso':
            env_vars['USE_SSO'] = 'true'
        else:
            env_vars['USE_SSO'] = 'false'
            env_vars['GRADESCOPE_USERNAME'] = self.get('gradescope.username', '')
            env_vars['GRADESCOPE_PASSWORD'] = self.get('gradescope.password', '')

        # Calendar settings
        env_vars['ENABLE_GOOGLE_CALENDAR'] = str(self.get('calendars.google.enabled', False)).lower()
        env_vars['ENABLE_NOTION'] = str(self.get('calendars.notion.enabled', False)).lower()

        if self.get('calendars.google.enabled'):
            env_vars['GOOGLE_CALENDAR_ID'] = self.get('calendars.google.calendar_id', 'primary')

        if self.get('calendars.notion.enabled'):
            env_vars['NOTION_TOKEN'] = self.get('calendars.notion.token', '')
            env_vars['NOTION_DATABASE_ID'] = self.get('calendars.notion.database_id', '')

        # Sync settings
        env_vars['TIME_WINDOW_DAYS'] = str(self.get('sync.time_window', 30))

        # Advanced settings
        env_vars['DRY_RUN'] = str(self.get('advanced.dry_run', False)).lower()
        env_vars['DEBUG_MODE'] = str(self.get('advanced.debug_mode', False)).lower()
        env_vars['HEADLESS'] = str(self.get('advanced.browser_headless', True)).lower()

        return env_vars

    def auto_detect_university(self) -> Optional[str]:
        """Auto-detect university from email domain"""
        email = self.get('user.email', '')
        if not email or '@' not in email:
            return None

        domain = email.split('@')[1].lower()

        # Common university domain mappings
        university_mappings = {
            'stanford.edu': 'Stanford University',
            'berkeley.edu': 'UC Berkeley',
            'ucla.edu': 'UCLA',
            'mit.edu': 'MIT',
            'harvard.edu': 'Harvard University',
            'yale.edu': 'Yale University',
            'princeton.edu': 'Princeton University',
            'columbia.edu': 'Columbia University',
            'nyu.edu': 'New York University',
            'usc.edu': 'USC',
            'northwestern.edu': 'Northwestern University',
            'uchicago.edu': 'University of Chicago',
            # Add more as needed
        }

        # Check for exact match
        if domain in university_mappings:
            return university_mappings[domain]

        # Check for .edu domains and extract university name
        if domain.endswith('.edu'):
            # Remove common prefixes/suffixes and convert to title case
            name = domain.replace('.edu', '').replace('www.', '')
            # Convert something like "stanford" to "Stanford University"
            if '.' not in name:  # Simple single-word domains
                return f"{name.title()} University"

        return None

    def get_smart_defaults(self) -> Dict[str, Any]:
        """Generate smart defaults based on detected settings"""
        smart_config = self.defaults.copy()

        # Auto-detect university
        university = self.auto_detect_university()
        if university:
            smart_config['user']['university'] = university

        return smart_config


def create_config_from_legacy_env() -> ConfigManager:
    """Create new config.yaml from existing .env file"""
    config_manager = ConfigManager()

    # Check if .env exists
    env_path = Path('.env')
    if not env_path.exists():
        logger.info("No .env file found, creating fresh configuration")
        config_manager.save_defaults()
        return config_manager

    logger.info("Converting existing .env to config.yaml")

    # Load .env file
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')

    # Convert to new format
    config = config_manager.defaults.copy()

    # Map legacy variables
    if 'USER_EMAIL' in env_vars:
        config['user']['email'] = env_vars['USER_EMAIL']

    if env_vars.get('USE_SSO', 'true').lower() == 'false':
        config['gradescope']['method'] = 'direct'
        config['gradescope']['username'] = env_vars.get('GRADESCOPE_USERNAME', '')
        config['gradescope']['password'] = env_vars.get('GRADESCOPE_PASSWORD', '')

    if env_vars.get('ENABLE_GOOGLE_CALENDAR', 'false').lower() == 'true':
        config['calendars']['google']['enabled'] = True
        config['calendars']['google']['calendar_id'] = env_vars.get('GOOGLE_CALENDAR_ID', 'primary')

    if env_vars.get('ENABLE_NOTION', 'false').lower() == 'true':
        config['calendars']['notion']['enabled'] = True
        config['calendars']['notion']['token'] = env_vars.get('NOTION_TOKEN', '')
        config['calendars']['notion']['database_id'] = env_vars.get('NOTION_DATABASE_ID', '')

    config['sync']['time_window'] = int(env_vars.get('TIME_WINDOW_DAYS', 30))
    config['advanced']['dry_run'] = env_vars.get('DRY_RUN', 'false').lower() == 'true'
    config['advanced']['debug_mode'] = env_vars.get('DEBUG_MODE', 'false').lower() == 'true'
    config['advanced']['browser_headless'] = env_vars.get('HEADLESS', 'true').lower() == 'true'

    # Save new config
    config_manager.config = config
    config_manager.save()

    # Backup old .env
    os.rename('.env', '.env.backup')
    logger.info("Legacy .env backed up to .env.backup")

    return config_manager


if __name__ == "__main__":
    # Test the configuration manager
    config = ConfigManager()
    config.load()

    print("Current configuration:")
    print(yaml.dump(config.config, default_flow_style=False, indent=2))

    is_valid, issues = config.validate()
    if not is_valid:
        print("\nConfiguration issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nConfiguration is valid!")