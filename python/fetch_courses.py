#!/usr/bin/env python3
"""Fetch course information for course selection interface"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from combined_scraper import GradescopeAssignmentFetcher
from course_selector import CourseSelector
from utils import logger

def fetch_courses_for_selection():
    """Fetch all courses and assignments for course selection interface"""
    
    print("🔍 Fetching courses for selection...")
    
    try:
        # Fetch all assignments
        fetcher = GradescopeAssignmentFetcher()
        assignments = fetcher.fetch_all_assignments()
        
        if not assignments:
            print("❌ No assignments found")
            return False
        
        print(f"📊 Found {len(assignments)} total assignments")
        
        # Extract course information
        selector = CourseSelector()
        courses_info = selector.get_course_info_from_assignments(assignments)
        
        print(f"📚 Extracted {len(courses_info)} courses")
        
        # Format course data for frontend
        course_list = []
        for course_name, info in courses_info.items():
            # Format assignment date range
            date_range = ""
            if info['first_assignment'] and info['last_assignment']:
                first_date = info['first_assignment'].strftime('%b %Y')
                last_date = info['last_assignment'].strftime('%b %Y')
                if first_date == last_date:
                    date_range = first_date
                else:
                    date_range = f"{first_date} - {last_date}"
            
            course_data = {
                'name': course_name,
                'assignment_count': info['assignment_count'],
                'date_range': date_range,
                'sample_assignments': info['sample_assignments'][:3]  # First 3 assignments
            }
            course_list.append(course_data)
        
        # Sort courses by assignment count (most assignments first)
        course_list.sort(key=lambda x: x['assignment_count'], reverse=True)
        
        # Output course data in format that Electron can parse
        print(f"COURSE_DATA:{json.dumps(course_list)}")
        
        print("✅ Course data prepared for selection interface")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching courses: {e}")
        logger.error(f"Course fetch error: {e}")
        return False

if __name__ == '__main__':
    success = fetch_courses_for_selection()
    sys.exit(0 if success else 1)