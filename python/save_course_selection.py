#!/usr/bin/env python3
"""Save course selection from frontend"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from course_selector import CourseSelector

def save_course_selection():
    """Save course selection from command line argument"""
    
    if len(sys.argv) < 2:
        print("❌ No course selection provided")
        return False
    
    try:
        # Parse course selection from command line argument
        selection_json = sys.argv[1]
        selected_courses = json.loads(selection_json)
        
        print(f"💾 Saving selection of {len(selected_courses)} courses...")
        
        # Save using CourseSelector
        selector = CourseSelector()
        success = selector.save_selection(set(selected_courses))
        
        if success:
            print("✅ Course selection saved successfully")
            for course in selected_courses:
                print(f"   • {course}")
            return True
        else:
            print("❌ Failed to save course selection")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid course selection data: {e}")
        return False
    except Exception as e:
        print(f"❌ Error saving course selection: {e}")
        return False

if __name__ == '__main__':
    success = save_course_selection()
    sys.exit(0 if success else 1)