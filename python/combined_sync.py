#!/usr/bin/env python3
"""Combined sync script that supports both ICS files and Notion Calendar"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add python directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from combined_scraper import GradescopeAssignmentFetcher
from ics_generator import ICSGenerator
from assignment_tracker import AssignmentTracker
from course_selector import CourseSelector
from notion_calendar import NotionCalendarSync
import config
from utils import logger


def combined_sync():
    """Enhanced sync function that supports both ICS and Notion Calendar"""
    
    print("📚 ASSIGNMENT CALENDAR SYNC (Enhanced)")
    print("="*60)
    
    # Check what's configured
    has_canvas = bool(config.CANVAS_API_TOKEN and config.CANVAS_API_URL)
    has_gradescope = True  # Always available
    has_notion = bool(config.NOTION_API_TOKEN and config.NOTION_DATABASE_ID)
    
    if not has_canvas:
        print("⚠️  Canvas not configured (optional)")
    
    print("📝 Sources available:")
    if has_canvas:
        print("   ✅ Canvas API")
    print("   ✅ Gradescope", "(SSO)" if config.GRADESCOPE_USE_SSO else "(Direct login)")
    
    print("📤 Output options:")
    print("   ✅ ICS Calendar File (always available)")
    if has_notion:
        print("   ✅ Notion Calendar (direct sync)")
    else:
        print("   ⚠️  Notion Calendar not configured (optional)")
    
    # Fetch assignments
    print("\n" + "-"*60)
    print("FETCHING ASSIGNMENTS...")
    print("-"*60)
    
    try:
        print("🌐 Fetching assignments from all sources...")
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
        
        # Show what we'll sync
        print("\n" + "-"*60)
        print("ASSIGNMENTS TO SYNC:")
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
        
        # Sync to available outputs
        print("\n" + "-"*60)
        print("SYNCING TO CALENDARS...")
        print("-"*60)
        
        sync_success = False
        
        # 1. Always generate ICS file
        print("📄 Creating ICS calendar file...")
        generator = ICSGenerator(timezone=config.TIMEZONE)
        
        # Add all assignments
        for assignment in upcoming:
            generator.add_assignment(assignment)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assignments_{timestamp}.ics"
        
        # Save file
        content = generator.generate_ics(filename)
        abs_path = os.path.abspath(filename)
        
        print("✅ ICS file created!")
        print("📂 File:", abs_path)
        print("📄 Size:", f"{len(content)} characters")
        print("📝 Events:", len(upcoming))
        sync_success = True
        
        # 2. Sync to Notion Calendar if configured
        if has_notion:
            print("\n🗓️  Syncing to Notion Calendar...")
            
            notion_sync = NotionCalendarSync()
            
            # Test connection first
            connection_test = notion_sync.test_connection()
            if connection_test["success"]:
                print(f"✅ Connected to Notion database: {connection_test.get('database_name', 'Unknown')}")
                
                # Sync assignments
                notion_result = notion_sync.sync_assignments(upcoming)
                
                if notion_result["success"]:
                    print(f"✅ {notion_result['message']}")
                    print("💡 Check your Notion Calendar to see the assignments!")
                else:
                    print(f"⚠️  Notion sync partially failed: {notion_result['message']}")
                    for error in notion_result.get("errors", []):
                        print(f"   {error}")
            else:
                print(f"❌ Notion connection failed: {connection_test['error']}")
                print("💡 ICS file is still available as backup")
        
        # Mark assignments as synced
        print("\n💾 Updating sync history...")
        for assignment in upcoming:
            tracker.mark_as_synced(assignment)
        tracker.save_data()
        
        # Final summary
        print("\n" + "="*60)
        print("📅 SYNC COMPLETE")
        print("="*60)
        
        if sync_success:
            print("✅ ICS Calendar File:")
            print(f"   📂 File: {abs_path}")
            print("   💡 Import into Google Calendar, Outlook, or any calendar app")
            
            if has_notion:
                print("\n✅ Notion Calendar:")
                print("   🗓️  Assignments synced directly to your Notion database")
                print("   💡 They should appear in Notion Calendar automatically")
            
            print(f"\n📊 Sync Summary:")
            print(f"   • {len(upcoming)} assignments synced")
            print(f"   • From {len(by_course)} selected courses")
            print(f"   • Due within next {days_ahead} days")
        
        print("="*60)
        
        return sync_success
        
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        logger.error(f"Sync error: {e}")
        return False


if __name__ == '__main__':
    success = combined_sync()
    sys.exit(0 if success else 1)