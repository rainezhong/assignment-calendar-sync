#!/usr/bin/env python3
"""
Electron-compatible sync script - no interactive prompts
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add python directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from combined_scraper import GradescopeAssignmentFetcher
from ics_generator import ICSGenerator
from assignment_tracker import AssignmentTracker
from semester_filter import SemesterFilter
from course_selector import CourseSelector
import config
from utils import logger


def electron_sync():
    """Main sync function for Electron - no interactive prompts"""
    
    print("📚 ASSIGNMENT CALENDAR SYNC")
    print("="*60)
    
    # Check what's configured
    has_canvas = bool(config.CANVAS_API_TOKEN and config.CANVAS_API_URL)
    has_gradescope = True  # Always available
    
    if not has_canvas:
        print("⚠️  Canvas not configured (optional)")
    
    print("📝 Sources available:")
    if has_canvas:
        print("   ✅ Canvas API")
    print("   ✅ Gradescope", "(SSO)" if config.GRADESCOPE_USE_SSO else "(Direct login)")
    
    # Fetch assignments
    print("\n" + "-"*60)
    print("FETCHING ASSIGNMENTS...")
    print("-"*60)
    
    try:
        print("🌐 Fetching real assignments from Canvas and Gradescope...")
        fetcher = GradescopeAssignmentFetcher()
        raw_assignments = fetcher.fetch_all_assignments()
        
        if not raw_assignments:
            print("❌ No assignments found")
            return False
        
        print(f"📊 Found {len(raw_assignments)} total assignments from all courses")
        
        # Initialize filtering systems
        tracker = AssignmentTracker()
        course_selector = CourseSelector()
        
        # Filter by user-selected courses
        print("🔍 Filtering by user-selected courses...")
        selected_assignments = course_selector.filter_assignments_by_selection(raw_assignments)
        
        if not selected_assignments:
            print("❌ No assignments found from selected courses")
            print("💡 Make sure you've selected courses in the app settings")
            print("💡 Go to ⚙️ Edit Settings to choose your current courses")
            return False
        
        print(f"📚 Found {len(selected_assignments)} assignments from selected courses")
        
        # Filter out duplicates (already synced)
        print("🔍 Checking for duplicate assignments...")
        new_assignments = tracker.filter_new_assignments(selected_assignments)
        
        if not new_assignments:
            print("✅ All current assignments have already been synced!")
            print("💡 Run this again when new assignments are posted")
            
            # Show sync summary
            summary = tracker.get_sync_summary()
            print(f"📈 Total assignments synced: {summary['total_synced']}")
            print(f"🕒 Last sync: {summary['last_sync']}")
            return True
        
        assignments = new_assignments
        print(f"📝 Found {len(assignments)} new assignments to sync")
        
        # Filter by date window (assignments due in near future)
        days_ahead = config.SYNC_DAYS_AHEAD
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        upcoming = [a for a in assignments 
                   if a.get('due_date') and a['due_date'].replace(tzinfo=None) <= cutoff_date]
        
        print(f"📅 {len(upcoming)} assignments due in next {days_ahead} days")
        
        if not upcoming:
            print("No assignments due in the selected time window")
            print(f"💡 Try increasing sync window beyond {days_ahead} days")
            return False
        
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
            print(f"📚 {course}:")
            for a in sorted(course_assignments, key=lambda x: x['due_date'] or datetime.max):
                if a['due_date']:
                    print(f"   • {a['name']} - Due: {a['due_date'].strftime('%b %d at %I:%M %p')}")
        
        # Generate calendar file
        print("\n" + "-"*60)
        print("CREATING CALENDAR FILE...")
        print("-"*60)
        
        generator = ICSGenerator(timezone=config.TIMEZONE)
        
        # Add all assignments
        for assignment in upcoming:
            generator.add_assignment(assignment)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assignments_{timestamp}.ics"
        
        # Save file
        content = generator.generate_ics(filename)
        
        # Get absolute path
        abs_path = os.path.abspath(filename)
        
        print("✅ Calendar file created!")
        print("📂 File:", abs_path)
        print("📄 Size:", f"{len(content)} characters")
        print("📝 Events:", len(upcoming))
        
        # Mark assignments as synced
        print("💾 Updating sync history...")
        for assignment in upcoming:
            tracker.mark_as_synced(assignment)
        tracker.save_data()
        
        print("\n" + "="*60)
        print("📅 CALENDAR FILE READY TO IMPORT")
        print("="*60)
        print(f"File: {abs_path}")
        print("\nImport instructions:")
        print("• Double-click the file to open in your default calendar app")
        print("• Or import manually into Google Calendar, Outlook, etc.")
        
        # Show sync summary
        summary = tracker.get_sync_summary()
        print(f"\n📈 Sync Summary:")
        print(f"• Total assignments tracked: {summary['total_synced']}")
        print(f"• History stored in: ~/.assignment_sync_history.json")
        print("="*60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        logger.error(f"Sync error: {e}")
        return False


if __name__ == '__main__':
    success = electron_sync()
    sys.exit(0 if success else 1)