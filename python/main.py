#!/usr/bin/env python3
"""
Assignment Calendar Sync - Main Script
Scrapes assignments from Gradescope and syncs them to Google Calendar
"""

import sys
import argparse
from datetime import datetime, timedelta
from combined_scraper import GradescopeAssignmentFetcher
from calendar_integration import GoogleCalendarIntegration  
from date_parser import parse_gradescope_date
import config
from utils import (
    logger, validate_credentials, log_system_info, 
    format_error_for_user, safe_cleanup,
    ConfigError, ScrapingError, CalendarError
)


def run_scraper(verbose=False):
    """Run the scraper to get assignments from Gradescope"""
    logger.info("Starting assignment fetcher for Gradescope...")
    
    fetcher = GradescopeAssignmentFetcher()
    
    try:
        # Get all assignments from Gradescope
        assignments = fetcher.fetch_all_assignments()
        
        logger.info(f"Found {len(assignments)} total assignments")
        
        return fetcher, assignments
        
    except Exception as e:
        if hasattr(fetcher, 'gradescope_scraper') and fetcher.gradescope_scraper:
            safe_cleanup(fetcher.gradescope_scraper.cleanup, "scraper")
        raise ScrapingError(f"Assignment fetching failed: {e}")


def parse_assignment_dates(assignments, verbose=False):
    """Parse and validate dates in assignments"""
    if verbose:
        print("📅 Parsing assignment dates...")
    
    parsed_assignments = []
    parsing_errors = 0
    
    for assignment in assignments:
        # Use our date parser for any date text we might have missed
        if assignment.get('due_date_text') and not assignment.get('due_date'):
            parsed_date = parse_gradescope_date(assignment['due_date_text'])
            if parsed_date:
                assignment['due_date'] = parsed_date
            else:
                parsing_errors += 1
                if verbose:
                    print(f"  ⚠️  Could not parse date: {assignment['due_date_text']}")
        
        parsed_assignments.append(assignment)
    
    if verbose and parsing_errors > 0:
        print(f"  ⚠️  {parsing_errors} dates could not be parsed")
    
    return parsed_assignments


def filter_assignments(assignments, days_ahead=None, verbose=False):
    """Filter assignments to upcoming ones within the specified timeframe"""
    if days_ahead is None:
        days_ahead = config.SYNC_DAYS_AHEAD
    
    if verbose:
        print(f"🗓️  Filtering assignments for next {days_ahead} days...")
    
    now = datetime.now()
    cutoff_date = now + timedelta(days=days_ahead)
    
    upcoming = []
    past_due = 0
    no_date = 0
    too_far = 0
    
    for assignment in assignments:
        if not assignment.get('due_date'):
            no_date += 1
            continue
        
        due_date = assignment['due_date']
        
        if due_date < now:
            past_due += 1
        elif due_date > cutoff_date:
            too_far += 1
        else:
            upcoming.append(assignment)
    
    if verbose:
        print(f"  ✅ {len(upcoming)} assignments due in next {days_ahead} days")
        print(f"  ⏰ {past_due} assignments already past due")
        print(f"  📅 {no_date} assignments without due dates") 
        print(f"  🔮 {too_far} assignments due after {days_ahead} days")
    
    return upcoming


def create_calendar_events(assignments, dry_run=False, verbose=False):
    """Create Google Calendar events for assignments"""
    if not assignments:
        print("No assignments to sync to calendar")
        return 0, 0
    
    if dry_run:
        print(f"🏃 DRY RUN MODE - Would sync {len(assignments)} assignments:")
        for assignment in assignments:
            course = assignment.get('course', 'Unknown Course')
            name = assignment.get('name', 'Unknown Assignment')
            due_date = assignment.get('due_date')
            
            if due_date:
                due_str = due_date.strftime('%Y-%m-%d %H:%M')
                print(f"  📝 {course}: {name}")
                print(f"     Due: {due_str}")
                if verbose and assignment.get('url'):
                    print(f"     Link: {assignment['url']}")
        
        return len(assignments), 0
    
    # Real sync mode
    if verbose:
        print("📅 Connecting to Google Calendar...")
    
    try:
        calendar = GoogleCalendarIntegration()
        
        if verbose:
            print("🔄 Syncing assignments to calendar...")
        
        created, skipped = calendar.sync_assignments(assignments)
        return created, skipped
        
    except Exception as e:
        raise Exception(f"Calendar sync failed: {e}")


def run_workflow(args):
    """Main workflow that ties everything together"""
    print("=" * 60)
    print("🎯 Assignment Calendar Sync")
    print("=" * 60)
    
    if args.verbose:
        log_system_info()
    
    scraper = None
    
    try:
        # Validate configuration first
        logger.info("Validating configuration...")
        validate_credentials()
        
        # Step 1: Scrape assignments from Gradescope
        print("\n📖 STEP 1: Scraping Gradescope assignments")
        print("-" * 40)
        scraper, raw_assignments = run_scraper(verbose=args.verbose)
        
        if not raw_assignments:
            logger.warning("No assignments found on Gradescope")
            print("No assignments found on Gradescope")
            return
        
        # Step 2: Parse and validate dates
        print(f"\n📅 STEP 2: Processing assignment dates") 
        print("-" * 40)
        assignments = parse_assignment_dates(raw_assignments, verbose=args.verbose)
        
        # Step 3: Filter assignments by date range
        print(f"\n🗓️  STEP 3: Filtering assignments")
        print("-" * 40)
        
        if args.all:
            filtered_assignments = [a for a in assignments if a.get('due_date')]
            logger.info(f"Including all {len(filtered_assignments)} assignments with due dates")
            if args.verbose:
                print(f"✅ Including all {len(filtered_assignments)} assignments with due dates")
        else:
            filtered_assignments = filter_assignments(
                assignments, 
                days_ahead=args.days, 
                verbose=args.verbose
            )
        
        # Step 4: Create calendar events
        print(f"\n📅 STEP 4: {'Simulating' if args.dry_run else 'Creating'} calendar events")
        print("-" * 40)
        
        created, skipped = create_calendar_events(
            filtered_assignments,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SYNC SUMMARY")
        print("=" * 60)
        print(f"  📚 Total assignments found: {len(raw_assignments)}")
        print(f"  🎯 Assignments in scope: {len(filtered_assignments)}")
        
        if args.dry_run:
            print(f"  🏃 Would create events: {created}")
            logger.info(f"Dry run completed - would create {created} events")
        else:
            print(f"  ✅ Events created: {created}")
            print(f"  ⏭️  Events skipped: {skipped}")
            logger.info(f"Sync completed - created {created} events, skipped {skipped}")
        
        print("=" * 60)
        print("🎉 Sync completed successfully!")
        
    except KeyboardInterrupt:
        logger.warning("Sync cancelled by user")
        print("\n\n⛔ Sync cancelled by user")
        sys.exit(1)
        
    except (ConfigError, ScrapingError, CalendarError) as e:
        # These are user-friendly errors, display them clearly
        error_msg = format_error_for_user(e)
        logger.error(str(e))
        print(f"\n\n{error_msg}")
        if args.verbose:
            logger.debug("Full error details:", exc_info=True)
        sys.exit(1)
        
    except Exception as e:
        # Unexpected errors
        error_msg = format_error_for_user(e, "Unexpected error")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n\n{error_msg}")
        if args.verbose:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        sys.exit(1)
        
    finally:
        if scraper and hasattr(scraper, 'gradescope_scraper') and scraper.gradescope_scraper:
            safe_cleanup(scraper.gradescope_scraper.cleanup, "scraper")


def main():
    """Main function with command line argument handling"""
    parser = argparse.ArgumentParser(
        description='Sync assignments from Gradescope to Google Calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py                    # Sync upcoming assignments
  python3 main.py --dry-run          # See what would be synced
  python3 main.py --verbose          # Show detailed output
  python3 main.py --days 14          # Sync assignments due in next 14 days
  python3 main.py --all              # Sync all assignments with due dates
        """
    )
    
    # Basic options
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Show what would be synced without creating calendar events'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true', 
        help='Show detailed output and progress information'
    )
    
    # Assignment filtering
    parser.add_argument(
        '--days', 
        type=int, 
        default=config.SYNC_DAYS_AHEAD,
        help=f'Number of days ahead to sync (default: {config.SYNC_DAYS_AHEAD})'
    )
    
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Sync all assignments with due dates (ignore --days limit)'
    )
    
    # Advanced options
    parser.add_argument(
        '--test-config',
        action='store_true',
        help='Test configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Handle test-config option
    if args.test_config:
        print("🔧 Testing configuration...")
        try:
            # Test config
            config.test_config()
            print("✅ Configuration is valid!")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            sys.exit(1)
        return
    
    # Run the main workflow
    run_workflow(args)


if __name__ == '__main__':
    main()