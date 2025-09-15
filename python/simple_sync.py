#!/usr/bin/env python3
"""
Simple Assignment Sync - No API keys required!
Just fetches assignments and creates a calendar file you can import.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add python directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from combined_scraper import GradescopeAssignmentFetcher
from ics_generator import ICSGenerator
import config
from utils import logger


def simple_sync():
    """Main function - super simple!"""
    
    print("\n" + "="*60)
    print("📚 ASSIGNMENT CALENDAR SYNC")
    print("="*60)
    print("This tool will fetch your assignments and create a calendar file")
    print("No Google API setup required!")
    print("="*60)
    
    # Check what's configured
    has_canvas = bool(config.CANVAS_API_TOKEN and config.CANVAS_API_URL)
    has_gradescope = True  # Always available with SSO
    
    if not has_canvas:
        print("\n⚠️  Canvas not configured (optional)")
        print("   To add Canvas, set CANVAS_API_TOKEN in .env")
    
    print("\n📝 Sources available:")
    if has_canvas:
        print("   ✅ Canvas API")
    print("   ✅ Gradescope", "(SSO)" if config.GRADESCOPE_USE_SSO else "(Direct login)")
    
    # Fetch assignments
    print("\n" + "-"*60)
    print("FETCHING ASSIGNMENTS...")
    print("-"*60)
    
    try:
        fetcher = GradescopeAssignmentFetcher()
        assignments = fetcher.fetch_all_assignments()
        
        if not assignments:
            print("\n❌ No assignments found")
            return
        
        # Filter to upcoming assignments only
        print(f"\n📊 Found {len(assignments)} total assignments")
        
        # Filter by date
        days_ahead = config.SYNC_DAYS_AHEAD
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        upcoming = [a for a in assignments 
                   if a.get('due_date') and a['due_date'].replace(tzinfo=None) <= cutoff_date]
        
        print(f"📅 {len(upcoming)} assignments due in next {days_ahead} days")
        
        if not upcoming:
            print("\nNo upcoming assignments to sync")
            return
        
        # Show what we'll create
        print("\n" + "-"*60)
        print("ASSIGNMENTS TO ADD TO CALENDAR:")
        print("-"*60)
        
        # Group by course
        by_course = {}
        for assignment in upcoming:
            course = assignment['course']
            if course not in by_course:
                by_course[course] = []
            by_course[course].append(assignment)
        
        for course, course_assignments in sorted(by_course.items()):
            print(f"\n📚 {course}:")
            for a in sorted(course_assignments, key=lambda x: x['due_date'] or datetime.max):
                if a['due_date']:
                    print(f"   • {a['name']} - Due: {a['due_date'].strftime('%b %d at %I:%M %p')}")
        
        # Generate calendar file
        print("\n" + "-"*60)
        print("CREATING CALENDAR FILE...")
        print("-"*60)
        
        generator = ICSGenerator(timezone=config.TIMEZONE)
        calendar_file = generator.save_and_open(upcoming)
        
        print("\n✅ Success! Your assignments are ready to import.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Make sure Chrome/Chromium is installed")
        print("3. Try running with --debug flag for more info")
        sys.exit(1)


if __name__ == '__main__':
    # Check for debug flag
    if '--debug' in sys.argv:
        config.DEBUG_MODE = True
    
    simple_sync()