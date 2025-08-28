"""Utility functions for error handling, logging, and retry logic"""

import os
import logging
import time
from functools import wraps
from datetime import datetime
import config


class SimpleLogger:
    """Simple logger that writes to both console and file"""
    
    def __init__(self, name="assignment_sync", log_file="sync.log"):
        self.name = name
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_path = os.path.join(log_dir, self.log_file)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if config.DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()  # Console output
            ]
        )
        
        self.logger = logging.getLogger(self.name)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
        if not config.DEBUG_MODE:
            print(f"ℹ️  {message}")
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
        print(f"❌ {message}")
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
        print(f"⚠️  {message}")
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
        if config.DEBUG_MODE:
            print(f"🔍 DEBUG: {message}")
    
    def success(self, message):
        """Log success message"""
        self.logger.info(f"SUCCESS: {message}")
        print(f"✅ {message}")


# Global logger instance
logger = SimpleLogger()


def retry_on_failure(max_attempts=3, delay=2, exceptions=(Exception,)):
    """
    Decorator to retry functions on failure with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (doubles each time)
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        break
                    
                    # Wait before retry with exponential backoff
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            
            # If we get here, all attempts failed
            raise last_exception
        
        return wrapper
    return decorator


class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass


class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass


class CalendarError(Exception):
    """Custom exception for calendar integration errors"""
    pass


def handle_common_errors(func):
    """Decorator to handle common errors with user-friendly messages"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
            
        except FileNotFoundError as e:
            if "chromedriver" in str(e).lower():
                logger.error("Chrome driver not found. Please install Chrome driver:")
                logger.error("  Mac: brew install chromedriver")
                logger.error("  Ubuntu: sudo apt-get install chromium-chromedriver")
                logger.error("  Or download from: https://chromedriver.chromium.org/")
            else:
                logger.error(f"File not found: {e}")
            raise
            
        except ImportError as e:
            if "selenium" in str(e).lower():
                logger.error("Selenium not installed. Please run: pip install -r requirements.txt")
            elif "google" in str(e).lower():
                logger.error("Google API libraries not installed. Please run: pip install -r requirements.txt")
            else:
                logger.error(f"Missing dependency: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            if config.DEBUG_MODE:
                import traceback
                logger.debug(traceback.format_exc())
            raise
    
    return wrapper


def validate_credentials():
    """Validate that all required credentials are present"""
    errors = []
    
    # Check Gradescope credentials
    if not config.GRADESCOPE_EMAIL:
        errors.append("GRADESCOPE_EMAIL is missing from .env file")
    
    if not config.GRADESCOPE_PASSWORD:
        errors.append("GRADESCOPE_PASSWORD is missing from .env file")
    
    # Check Google Calendar credentials  
    if not config.GOOGLE_CLIENT_ID:
        errors.append("GOOGLE_CLIENT_ID is missing from .env file")
    
    if not config.GOOGLE_CLIENT_SECRET:
        errors.append("GOOGLE_CLIENT_SECRET is missing from .env file")
    
    if errors:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("\nPlease check your .env file and add the missing credentials.")
        logger.error("Copy .env.example to .env if you haven't already.")
        raise ConfigError("Missing required credentials")
    
    logger.debug("Credential validation passed")


def handle_selenium_errors(e):
    """Provide user-friendly error messages for common Selenium issues"""
    error_msg = str(e).lower()
    
    if "chromedriver" in error_msg:
        return ("Chrome driver issue. Please ensure Chrome and ChromeDriver are installed:\n"
                "  Mac: brew install chromedriver\n" 
                "  Ubuntu: sudo apt-get install chromium-chromedriver")
    
    elif "no such element" in error_msg:
        return "Could not find expected element on page. Gradescope may have changed their layout."
    
    elif "timeout" in error_msg:
        return "Page took too long to load. Check your internet connection or try again later."
    
    elif "session not created" in error_msg:
        return "Could not start browser session. Check Chrome installation."
    
    elif "permission denied" in error_msg:
        return "Permission denied. Check file permissions or run with appropriate privileges."
    
    else:
        return f"Browser automation error: {e}"


def handle_google_api_errors(e):
    """Provide user-friendly error messages for Google API issues"""
    error_msg = str(e).lower()
    
    if "invalid_client" in error_msg:
        return ("Invalid Google Calendar credentials. Please check:\n"
                "  - GOOGLE_CLIENT_ID in .env file\n"
                "  - GOOGLE_CLIENT_SECRET in .env file\n"
                "  - Credentials are from Google Cloud Console")
    
    elif "invalid_grant" in error_msg:
        return ("Google authentication expired. Please delete token.json and re-authenticate.")
    
    elif "insufficient" in error_msg or "scope" in error_msg:
        return ("Insufficient permissions for Google Calendar. Please re-authenticate with full calendar access.")
    
    elif "quota" in error_msg or "rate" in error_msg:
        return ("Google API rate limit exceeded. Please wait a few minutes and try again.")
    
    elif "not found" in error_msg:
        return ("Calendar not found. Check GOOGLE_CALENDAR_ID in .env file or use 'primary' for main calendar.")
    
    else:
        return f"Google Calendar API error: {e}"


def check_network_connection():
    """Simple network connectivity check"""
    try:
        import urllib.request
        urllib.request.urlopen('http://www.google.com', timeout=5)
        return True
    except:
        return False


def safe_cleanup(cleanup_func, resource_name):
    """Safely call cleanup functions with error handling"""
    try:
        cleanup_func()
        logger.debug(f"Successfully cleaned up {resource_name}")
    except Exception as e:
        logger.warning(f"Error during {resource_name} cleanup: {e}")


def log_system_info():
    """Log system information for debugging"""
    import sys
    import platform
    
    logger.debug("=== System Information ===")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {platform.system()} {platform.release()}")
    logger.debug(f"Current time: {datetime.now()}")
    logger.debug(f"Debug mode: {config.DEBUG_MODE}")
    logger.debug("==========================")


def format_error_for_user(error, context=""):
    """Format error messages in a user-friendly way"""
    if isinstance(error, ConfigError):
        return f"❌ Configuration Error: {error}"
    
    elif isinstance(error, ScrapingError):
        return f"❌ Scraping Error: {error}"
    
    elif isinstance(error, CalendarError):
        return f"❌ Calendar Error: {error}"
    
    elif "selenium" in str(error).lower():
        return f"❌ Browser Error: {handle_selenium_errors(error)}"
    
    elif "google" in str(error).lower() or "api" in str(error).lower():
        return f"❌ Google Calendar Error: {handle_google_api_errors(error)}"
    
    else:
        base_msg = f"❌ {context + ': ' if context else ''}{error}"
        if not check_network_connection():
            return f"{base_msg}\n💡 Check your internet connection."
        return base_msg


# Export commonly used functions
__all__ = [
    'logger',
    'retry_on_failure', 
    'handle_common_errors',
    'validate_credentials',
    'handle_selenium_errors',
    'handle_google_api_errors',
    'check_network_connection',
    'safe_cleanup',
    'log_system_info',
    'format_error_for_user',
    'ConfigError',
    'ScrapingError', 
    'CalendarError'
]