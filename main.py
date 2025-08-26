#!/usr/bin/env python3
"""
Assignment Calendar Sync Tool - Main Entry Point

This module provides the command-line interface and orchestrates the synchronization
process between educational platforms and Google Calendar.
"""

import sys
import click
import logging
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utilities.config import Config
from utilities.logger import setup_logging
from scraping.universal_scraper import UniversalScraper
from data_processing.processor import AssignmentProcessor
from calendar_integration.sync_manager import CalendarSyncManager
from utilities.scheduler import SchedulerService

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx, debug):
    """Assignment Calendar Sync Tool - Automate your academic scheduling."""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    if debug:
        logger.info("Debug mode enabled")


@cli.command()
@click.option('--platform', '-p', help='Specific platform to sync')
@click.option('--dry-run', is_flag=True, help='Preview changes without syncing')
@click.pass_context
def sync(ctx, platform, dry_run):
    """Perform a one-time synchronization of assignments."""
    try:
        logger.info("Starting synchronization process...")
        
        # Initialize components
        config = Config()
        scraper = UniversalScraper(config)
        processor = AssignmentProcessor()
        calendar = CalendarSyncManager(config)
        
        # Scrape assignments
        if platform:
            logger.info(f"Scraping assignments from {platform}")
            raw_assignments = scraper.scrape_platform(platform)
        else:
            logger.info("Scraping assignments from all configured platforms")
            raw_assignments = scraper.scrape_all_platforms()
        
        # Process assignments
        logger.info("Processing scraped assignments...")
        assignments = processor.process(raw_assignments)
        
        if dry_run:
            logger.info("Dry run mode - displaying assignments without syncing:")
            for assignment in assignments:
                click.echo(f"  - {assignment['title']} (Due: {assignment['due_date']})")
            return
        
        # Sync to calendar
        logger.info("Syncing assignments to Google Calendar...")
        results = calendar.sync_assignments(assignments)
        
        logger.success(f"Successfully synced {results['created']} new assignments")
        logger.info(f"Updated {results['updated']} existing assignments")
        logger.info(f"Skipped {results['skipped']} unchanged assignments")
        
    except Exception as e:
        logger.error(f"Synchronization failed: {e}")
        if ctx.obj['DEBUG']:
            raise
        sys.exit(1)


@cli.command()
@click.option('--interval', '-i', default=6, help='Sync interval in hours')
@click.pass_context
def schedule(ctx, interval):
    """Start the automatic synchronization scheduler."""
    try:
        logger.info(f"Starting scheduler with {interval} hour interval...")
        
        config = Config()
        scheduler = SchedulerService(config, interval_hours=interval)
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        if ctx.obj['DEBUG']:
            raise
        sys.exit(1)


@cli.command()
@click.option('--days', '-d', default=7, help='Number of days to look ahead')
@click.pass_context
def list(ctx, days):
    """List upcoming assignments from the local database."""
    try:
        from utilities.database import Database
        from datetime import datetime, timedelta
        
        db = Database()
        end_date = datetime.now() + timedelta(days=days)
        
        assignments = db.get_upcoming_assignments(end_date)
        
        if not assignments:
            click.echo(f"No assignments due in the next {days} days")
            return
        
        click.echo(f"\nUpcoming assignments (next {days} days):\n")
        click.echo(f"{'Title':<40} {'Platform':<15} {'Due Date':<20}")
        click.echo("-" * 75)
        
        for assignment in assignments:
            title = assignment['title'][:37] + "..." if len(assignment['title']) > 40 else assignment['title']
            click.echo(f"{title:<40} {assignment['platform']:<15} {assignment['due_date']:<20}")
            
    except Exception as e:
        logger.error(f"Failed to list assignments: {e}")
        if ctx.obj['DEBUG']:
            raise
        sys.exit(1)


@cli.command()
@click.argument('name')
@click.argument('url')
@click.option('--scraper-type', '-t', default='generic', help='Type of scraper to use')
@click.pass_context
def add_platform(ctx, name, url, scraper_type):
    """Add a new educational platform to the configuration."""
    try:
        from utilities.config import Config
        
        config = Config()
        config.add_platform({
            'name': name,
            'url': url,
            'scraper': scraper_type,
            'credentials_required': True
        })
        
        logger.success(f"Successfully added platform: {name}")
        click.echo(f"Platform '{name}' has been added to configuration.")
        click.echo("You may need to provide credentials in the .env file.")
        
    except Exception as e:
        logger.error(f"Failed to add platform: {e}")
        if ctx.obj['DEBUG']:
            raise
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear the cache?')
@click.pass_context
def clear_cache(ctx):
    """Clear the local database cache."""
    try:
        from utilities.database import Database
        
        db = Database()
        db.clear_cache()
        
        logger.success("Cache cleared successfully")
        click.echo("Local cache has been cleared.")
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        if ctx.obj['DEBUG']:
            raise
        sys.exit(1)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the application with required configuration files."""
    try:
        from pathlib import Path
        import yaml
        
        # Create .env.example if it doesn't exist
        env_example = Path(".env.example")
        if not env_example.exists():
            env_content = """# Google Calendar API
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
CALENDAR_ID=primary

# Database
DATABASE_URL=sqlite:///assignments.db

# Scraping Configuration
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30

# Scheduling
SYNC_INTERVAL_HOURS=6
REMINDER_MINUTES=1440

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/sync.log

# Platform Credentials (add as needed)
# CANVAS_USERNAME=your_username
# CANVAS_PASSWORD=your_password
"""
            env_example.write_text(env_content)
            logger.info("Created .env.example")
        
        # Create platforms.yaml if it doesn't exist
        platforms_file = Path("config/platforms.yaml")
        if not platforms_file.exists():
            platforms_config = {
                'platforms': [
                    {
                        'name': 'Canvas',
                        'url': 'https://canvas.yourschool.edu',
                        'scraper': 'canvas_scraper',
                        'credentials_required': True
                    },
                    {
                        'name': 'Blackboard',
                        'url': 'https://blackboard.yourschool.edu',
                        'scraper': 'blackboard_scraper',
                        'credentials_required': True
                    }
                ]
            }
            platforms_file.parent.mkdir(exist_ok=True)
            with open(platforms_file, 'w') as f:
                yaml.dump(platforms_config, f, default_flow_style=False)
            logger.info("Created config/platforms.yaml")
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        logger.success("Initialization complete!")
        click.echo("\nInitialization complete! Next steps:")
        click.echo("1. Copy .env.example to .env and fill in your credentials")
        click.echo("2. Edit config/platforms.yaml with your educational platforms")
        click.echo("3. Set up Google Calendar API credentials")
        click.echo("4. Run 'python main.py sync' to test the synchronization")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        if ctx.obj['DEBUG']:
            raise
        sys.exit(1)


def main():
    """Main entry point for the application."""
    cli(obj={})


if __name__ == "__main__":
    main()