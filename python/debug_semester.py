#!/usr/bin/env python3
"""Debug script to analyze semester filtering"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from semester_filter import SemesterFilter
from combined_scraper import GradescopeAssignmentFetcher

def debug_semester_filtering():
    print("🔍 DEBUGGING SEMESTER FILTERING")
    print("="*60)
    
    # Initialize components
    sf = SemesterFilter()
    current_semester, current_year = sf.detect_current_semester()
    
    print(f"📅 Current semester detected: {current_semester} {current_year}")
    print()
    
    # Fetch real assignments
    print("🌐 Fetching assignments from Gradescope...")
    fetcher = GradescopeAssignmentFetcher()
    assignments = fetcher.fetch_all_assignments()
    
    print(f"📊 Total assignments fetched: {len(assignments)}")
    print()
    
    # Analyze course names
    print("📚 COURSE NAMES ANALYSIS:")
    print("-" * 40)
    
    unique_courses = set()
    for assignment in assignments:
        course = assignment.get('course', 'Unknown')
        unique_courses.add(course)
    
    for course in sorted(unique_courses):
        extracted = sf.extract_semester_from_course(course)
        is_target = sf.is_target_semester(course, current_semester, current_year)
        status = "✅ INCLUDED" if is_target else "❌ EXCLUDED"
        
        print(f"  {status} | {course}")
        print(f"            └─ Extracted: {extracted}")
        print()
    
    # Filter assignments
    print("🔍 FILTERING RESULTS:")
    print("-" * 40)
    
    filtered = sf.filter_assignments_by_semester(assignments, current_semester, current_year)
    
    print(f"📊 Original: {len(assignments)} assignments")
    print(f"📊 Filtered: {len(filtered)} assignments")
    print(f"📊 Excluded: {len(assignments) - len(filtered)} assignments")
    
    # Show sample filtered assignments
    print("\n📝 SAMPLE FILTERED ASSIGNMENTS:")
    print("-" * 40)
    
    for assignment in filtered[:10]:  # Show first 10
        course = assignment.get('course', 'Unknown')
        name = assignment.get('name', 'Unknown')
        due_date = assignment.get('due_date')
        due_str = due_date.strftime('%Y-%m-%d') if due_date else 'No due date'
        
        print(f"  • {course}: {name} (Due: {due_str})")
    
    if len(filtered) > 10:
        print(f"  ... and {len(filtered) - 10} more assignments")

if __name__ == '__main__':
    debug_semester_filtering()