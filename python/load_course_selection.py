#!/usr/bin/env python3
"""Load saved course selection for frontend"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from course_selector import CourseSelector

def load_course_selection():
    """Load saved course selection and output for Electron"""
    
    try:
        selector = CourseSelector()
        selected_courses = selector.load_selection()
        
        # Convert set to list for JSON serialization
        selection_list = list(selected_courses)
        
        print(f"📂 Loaded selection of {len(selection_list)} courses")
        
        # Output selection data in format that Electron can parse
        print(f"SELECTION_DATA:{json.dumps(selection_list)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading course selection: {e}")
        return False

if __name__ == '__main__':
    success = load_course_selection()
    sys.exit(0 if success else 1)