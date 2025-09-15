#!/usr/bin/env python3
"""Course selection system for manual filtering"""

import json
import os
from typing import List, Dict, Set
from pathlib import Path
from utils import logger

class CourseSelector:
    """Manages user course selection for filtering"""
    
    def __init__(self):
        # Store selection in home directory
        self.selection_file = Path.home() / '.assignment_calendar_course_selection.json'
    
    def get_course_info_from_assignments(self, assignments: List[Dict]) -> Dict[str, Dict]:
        """Extract course info from assignments"""
        courses = {}
        
        for assignment in assignments:
            course_name = assignment.get('course', 'Unknown')
            
            if course_name not in courses:
                courses[course_name] = {
                    'name': course_name,
                    'assignment_count': 0,
                    'first_assignment': None,
                    'last_assignment': None,
                    'sample_assignments': []
                }
            
            # Update course info
            course_info = courses[course_name]
            course_info['assignment_count'] += 1
            
            # Track date range
            due_date = assignment.get('due_date')
            if due_date:
                if not course_info['first_assignment'] or due_date < course_info['first_assignment']:
                    course_info['first_assignment'] = due_date
                if not course_info['last_assignment'] or due_date > course_info['last_assignment']:
                    course_info['last_assignment'] = due_date
            
            # Keep sample assignment names
            if len(course_info['sample_assignments']) < 3:
                course_info['sample_assignments'].append(assignment.get('name', 'Unnamed'))
        
        return courses
    
    def save_selection(self, selected_courses: Set[str]) -> bool:
        """Save user course selection to file"""
        try:
            selection_data = {
                'selected_courses': list(selected_courses),
                'last_updated': str(Path().cwd()),  # Simple timestamp substitute
                'version': '1.0'
            }
            
            with open(self.selection_file, 'w') as f:
                json.dump(selection_data, f, indent=2)
            
            logger.info(f"Saved course selection: {len(selected_courses)} courses")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save course selection: {e}")
            return False
    
    def load_selection(self) -> Set[str]:
        """Load user course selection from file"""
        try:
            if not self.selection_file.exists():
                return set()
            
            with open(self.selection_file, 'r') as f:
                selection_data = json.load(f)
            
            selected_courses = set(selection_data.get('selected_courses', []))
            logger.info(f"Loaded course selection: {len(selected_courses)} courses")
            return selected_courses
            
        except Exception as e:
            logger.error(f"Failed to load course selection: {e}")
            return set()
    
    def filter_assignments_by_selection(self, assignments: List[Dict], selected_courses: Set[str] = None) -> List[Dict]:
        """Filter assignments to only include selected courses"""
        
        if selected_courses is None:
            selected_courses = self.load_selection()
        
        if not selected_courses:
            logger.warning("No courses selected - all assignments will be excluded")
            return []
        
        # Filter assignments
        filtered = []
        for assignment in assignments:
            course_name = assignment.get('course', '')
            if course_name in selected_courses:
                filtered.append(assignment)
        
        # Log results
        original_count = len(assignments)
        filtered_count = len(filtered)
        excluded_count = original_count - filtered_count
        
        logger.info(f"Course selection filter:")
        logger.info(f"  Selected {len(selected_courses)} courses")
        logger.info(f"  Included {filtered_count} assignments")
        logger.info(f"  Excluded {excluded_count} assignments")
        
        # Debug: show which courses are selected
        for course in sorted(selected_courses):
            course_assignments = [a for a in assignments if a.get('course') == course]
            logger.debug(f"  ✅ {course}: {len(course_assignments)} assignments")
        
        return filtered
    
    def get_selection_summary(self) -> Dict:
        """Get summary of current selection for display"""
        selected_courses = self.load_selection()
        
        return {
            'has_selection': len(selected_courses) > 0,
            'selected_count': len(selected_courses),
            'selected_courses': sorted(list(selected_courses)),
            'selection_file_exists': self.selection_file.exists()
        }

def test_course_selector():
    """Test the course selector functionality"""
    
    # Sample assignments for testing
    test_assignments = [
        {'course': 'CS 61A', 'name': 'Lab 1', 'due_date': None},
        {'course': 'CS 61A', 'name': 'HW 1', 'due_date': None},
        {'course': 'CS 61B', 'name': 'Project 1', 'due_date': None},
        {'course': 'MATH 53', 'name': 'HW 1', 'due_date': None},
        {'course': 'EECS 16A', 'name': 'Lab 1', 'due_date': None},
    ]
    
    selector = CourseSelector()
    
    # Test course info extraction
    print("📚 Course Information:")
    course_info = selector.get_course_info_from_assignments(test_assignments)
    for course, info in course_info.items():
        print(f"  {course}: {info['assignment_count']} assignments")
    
    # Test selection save/load
    test_selection = {'CS 61A', 'MATH 53'}
    print(f"\n💾 Saving selection: {test_selection}")
    selector.save_selection(test_selection)
    
    loaded_selection = selector.load_selection()
    print(f"📂 Loaded selection: {loaded_selection}")
    
    # Test filtering
    filtered = selector.filter_assignments_by_selection(test_assignments, test_selection)
    print(f"\n🔍 Filtered assignments: {len(filtered)}")
    for assignment in filtered:
        print(f"  • {assignment['course']}: {assignment['name']}")

if __name__ == '__main__':
    test_course_selector()