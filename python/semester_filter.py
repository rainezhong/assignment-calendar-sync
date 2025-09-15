"""Semester detection and filtering system"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils import logger


class SemesterFilter:
    """Handles semester detection and filtering of assignments"""
    
    def __init__(self):
        self.current_date = datetime.now()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
    
    def detect_current_semester(self) -> Tuple[str, int]:
        """
        Detect current semester based on current date using ACADEMIC YEAR logic
        Returns: (semester_name, academic_year)
        """
        month = self.current_month
        calendar_year = self.current_year
        
        # Academic semester detection logic:
        # January - May: Spring semester (same calendar year)
        # June - August: Summer semester (same calendar year)
        # September - December: Fall semester (ACADEMIC YEAR starts with fall)
        
        if 1 <= month <= 5:
            # Spring: January-May uses same calendar year
            return ("Spring", calendar_year)
        elif 6 <= month <= 8:
            # Summer: June-August uses same calendar year  
            return ("Summer", calendar_year)
        else:  # September-December
            # Fall: Uses current calendar year
            # Example: Sep 2025 = Fall 2025
            # This matches how your school names their semesters
            return ("Fall", calendar_year)
    
    def get_semester_variants(self, semester: str, year: int) -> List[str]:
        """Get all possible ways a semester might be written"""
        year_2digit = str(year)[-2:]
        
        variants = []
        
        if semester.lower() == "spring":
            variants = [
                f"Spring {year}",
                f"spring {year}",
                f"SPRING {year}",
                f"Sp {year}",
                f"sp {year}",
                f"SP {year}",
                f"Spring{year}",
                f"Sp{year}",
                f"SP{year}",
                f"sp{year}",
                f"Spring {year_2digit}",
                f"Sp {year_2digit}",
                f"SP {year_2digit}",
                f"sp{year_2digit}",
                f"SP{year_2digit}",
                f"Sp{year_2digit}",
                f"spring{year_2digit}",
                # Alternative formats
                f"S{year}",
                f"S{year_2digit}",
                f"{year} Spring",
                f"{year} Sp",
                f"{year_2digit} Spring",
                f"{year_2digit} Sp"
            ]
        elif semester.lower() == "summer":
            variants = [
                f"Summer {year}",
                f"summer {year}",
                f"SUMMER {year}",
                f"Su {year}",
                f"su {year}",
                f"SU {year}",
                f"Summer{year}",
                f"Su{year}",
                f"SU{year}",
                f"su{year}",
                f"Summer {year_2digit}",
                f"Su {year_2digit}",
                f"SU {year_2digit}",
                f"su{year_2digit}",
                f"SU{year_2digit}",
                f"Su{year_2digit}",
                f"summer{year_2digit}",
                f"U{year}",
                f"U{year_2digit}",
                f"{year} Summer",
                f"{year} Su",
                f"{year_2digit} Summer",
                f"{year_2digit} Su"
            ]
        elif semester.lower() == "fall":
            variants = [
                f"Fall {year}",
                f"fall {year}",
                f"FALL {year}",
                f"Fa {year}",
                f"fa {year}",
                f"FA {year}",
                f"Fall{year}",
                f"Fa{year}",
                f"FA{year}",
                f"fa{year}",
                f"Fall {year_2digit}",
                f"Fa {year_2digit}",
                f"FA {year_2digit}",
                f"fa{year_2digit}",
                f"FA{year_2digit}",
                f"Fa{year_2digit}",
                f"fall{year_2digit}",
                # Alternative formats
                f"F{year}",
                f"F{year_2digit}",
                f"{year} Fall",
                f"{year} Fa",
                f"{year_2digit} Fall",
                f"{year_2digit} Fa"
            ]
        
        return variants
    
    def extract_semester_from_course(self, course_name: str) -> Optional[Tuple[str, int]]:
        """
        Extract semester and year from course name
        Returns: (semester, year) or None if not found
        """
        course_lower = course_name.lower()
        
        # Define semester patterns with regex
        patterns = [
            # Spring patterns
            (r'spring\s*(\d{4})', 'Spring'),
            (r'sp\s*(\d{4})', 'Spring'),
            (r's(\d{4})', 'Spring'),
            (r'spring\s*(\d{2})', 'Spring'),
            (r'sp\s*(\d{2})', 'Spring'),
            (r's(\d{2})', 'Spring'),
            
            # Fall patterns  
            (r'fall\s*(\d{4})', 'Fall'),
            (r'fa\s*(\d{4})', 'Fall'),
            (r'f(\d{4})', 'Fall'),
            (r'fall\s*(\d{2})', 'Fall'),
            (r'fa\s*(\d{2})', 'Fall'),
            (r'f(\d{2})', 'Fall'),
            
            # Summer patterns
            (r'summer\s*(\d{4})', 'Summer'),
            (r'su\s*(\d{4})', 'Summer'),
            (r'u(\d{4})', 'Summer'),
            (r'summer\s*(\d{2})', 'Summer'),
            (r'su\s*(\d{2})', 'Summer'),
            (r'u(\d{2})', 'Summer'),
            
            # Year first patterns
            (r'(\d{4})\s*spring', 'Spring'),
            (r'(\d{4})\s*fall', 'Fall'),
            (r'(\d{4})\s*summer', 'Summer'),
            (r'(\d{2})\s*spring', 'Spring'),
            (r'(\d{2})\s*fall', 'Fall'),
            (r'(\d{2})\s*summer', 'Summer'),
        ]
        
        for pattern, semester in patterns:
            match = re.search(pattern, course_lower)
            if match:
                year_str = match.group(1)
                try:
                    year = int(year_str)
                    # Convert 2-digit year to 4-digit
                    if year < 100:
                        if year < 50:  # Assume 20xx
                            year += 2000
                        else:  # Assume 19xx
                            year += 1900
                    
                    logger.debug(f"Extracted semester from '{course_name}': {semester} {year}")
                    return (semester, year)
                except ValueError:
                    continue
        
        return None
    
    def get_semester_from_date(self, date) -> Tuple[str, int]:
        """
        Determine semester from assignment due date
        Returns: (semester_name, year)
        """
        month = date.month
        year = date.year
        
        # Semester logic based on due date:
        # January - May: Spring semester
        # June - August: Summer semester
        # September - December: Fall semester
        
        if 1 <= month <= 5:
            return ("Spring", year)
        elif 6 <= month <= 8:
            return ("Summer", year)
        else:  # 9-12
            return ("Fall", year)
    
    def is_target_semester(self, course_name: str, target_semester: str, target_year: int, due_date=None) -> bool:
        """
        Check if a course belongs to the target semester
        Uses due date analysis when course name lacks semester info
        """
        extracted = self.extract_semester_from_course(course_name)
        if extracted:
            semester, year = extracted
            return semester.lower() == target_semester.lower() and year == target_year
        
        # If no explicit semester in course name, use due date to determine semester
        if due_date:
            assignment_semester, assignment_year = self.get_semester_from_date(due_date)
            logger.debug(f"Course '{course_name}' due date {due_date.strftime('%Y-%m-%d')} → {assignment_semester} {assignment_year}")
            return (assignment_semester.lower() == target_semester.lower() and 
                   assignment_year == target_year)
        
        # If no due date available and no semester in name, exclude to be safe
        logger.debug(f"Course '{course_name}' has no semester info and no due date - excluding")
        return False
    
    def get_available_semesters(self) -> List[Tuple[str, int]]:
        """
        Get list of available semester options for user selection
        """
        current_semester, current_year = self.detect_current_semester()
        
        semesters = []
        
        # Current semester
        semesters.append((current_semester, current_year))
        
        # Previous semester
        if current_semester == "Spring":
            semesters.append(("Fall", current_year - 1))
        elif current_semester == "Summer":
            semesters.append(("Spring", current_year))
        else:  # Fall
            semesters.append(("Summer", current_year))
        
        # Next semester (if we're early in current semester)
        if current_semester == "Spring":
            semesters.append(("Summer", current_year))
        elif current_semester == "Summer":
            semesters.append(("Fall", current_year))
        else:  # Fall
            semesters.append(("Spring", current_year + 1))
        
        return semesters
    
    def determine_course_semester(self, course_assignments: List[Dict]) -> Tuple[str, int]:
        """
        Determine semester for a course based on assignment due date clustering
        """
        if not course_assignments:
            return None
            
        # Count assignments by semester periods
        spring_count = 0  # Jan-May
        summer_count = 0  # Jun-Aug  
        fall_count = 0    # Sep-Dec
        years = []
        
        for assignment in course_assignments:
            due_date = assignment.get('due_date')
            if not due_date:
                continue
                
            month = due_date.month
            year = due_date.year
            years.append(year)
            
            if 1 <= month <= 5:
                spring_count += 1
            elif 6 <= month <= 8:
                summer_count += 1
            else:  # 9-12
                fall_count += 1
        
        if not years:
            return None
            
        # Use most common year
        most_common_year = max(set(years), key=years.count)
        
        # Determine semester based on majority of assignments
        total_with_dates = spring_count + summer_count + fall_count
        if total_with_dates == 0:
            return None
            
        spring_pct = spring_count / total_with_dates
        summer_pct = summer_count / total_with_dates  
        fall_pct = fall_count / total_with_dates
        
        # Require at least 60% of assignments in one semester period
        if spring_pct >= 0.6:
            return ("Spring", most_common_year)
        elif summer_pct >= 0.6:
            return ("Summer", most_common_year)
        elif fall_pct >= 0.6:
            return ("Fall", most_common_year)
        else:
            # Mixed semester course - use the plurality
            if spring_count >= summer_count and spring_count >= fall_count:
                return ("Spring", most_common_year)
            elif summer_count >= fall_count:
                return ("Summer", most_common_year)
            else:
                return ("Fall", most_common_year)

    def filter_assignments_by_semester(self, assignments: List[Dict], 
                                     target_semester: str, target_year: int) -> List[Dict]:
        """
        Filter assignments to only include those from target semester
        Uses assignment date clustering to determine course semesters
        """
        # Group assignments by course
        courses_assignments = {}
        for assignment in assignments:
            course = assignment.get('course', '')
            if course not in courses_assignments:
                courses_assignments[course] = []
            courses_assignments[course].append(assignment)
        
        # Determine semester for each course using assignment clustering
        course_semesters = {}
        for course, course_assignments in courses_assignments.items():
            semester_info = self.determine_course_semester(course_assignments)
            course_semesters[course] = semester_info
            
            if semester_info:
                semester, year = semester_info
                logger.debug(f"Course '{course}' classified as: {semester} {year}")
            else:
                logger.debug(f"Course '{course}' could not be classified")
        
        # Filter assignments based on course semester classifications
        filtered = []
        excluded_courses = set()
        included_courses = set()
        
        for assignment in assignments:
            course = assignment.get('course', '')
            semester_info = course_semesters.get(course)
            
            if semester_info:
                semester, year = semester_info
                is_target = (semester.lower() == target_semester.lower() and year == target_year)
            else:
                # If we can't classify the course, exclude it to be safe
                is_target = False
            
            if is_target:
                filtered.append(assignment)
                included_courses.add(course)
            else:
                excluded_courses.add(course)
        
        # Log filtering results
        logger.info(f"Semester filter ({target_semester} {target_year}):")
        logger.info(f"  Included {len(filtered)} assignments from {len(included_courses)} courses")
        logger.info(f"  Excluded assignments from {len(excluded_courses)} courses")
        
        # Log debug details if we have courses to show
        if len(included_courses) < 10:  # Only show if not too many
            for course in sorted(included_courses):
                logger.debug(f"  ✅ Included: {course}")
        if len(excluded_courses) < 10:
            for course in sorted(excluded_courses):
                logger.debug(f"  ❌ Excluded: {course}")
        
        return filtered


def test_semester_filter():
    """Test the semester filter functionality"""
    print("Testing Semester Filter...")
    
    filter_sys = SemesterFilter()
    
    # Test current semester detection
    current_semester, current_year = filter_sys.detect_current_semester()
    print(f"Current semester: {current_semester} {current_year}")
    
    # Test semester extraction
    test_courses = [
        "CS 101 - Fall 2024",
        "MATH 150 - Spring 2024", 
        "PHYS 201 Fall2024",
        "ENG 102 Sp24",
        "HIST 101 F24",
        "CHEM 101",  # No semester
        "BIO 200 - Spring 2023",
        "CS 301 2024 Fall"
    ]
    
    print("\nTesting semester extraction:")
    for course in test_courses:
        result = filter_sys.extract_semester_from_course(course)
        print(f"  {course} → {result}")
    
    # Test filtering
    test_assignments = [
        {'name': 'Assignment 1', 'course': 'CS 101 - Fall 2024'},
        {'name': 'Assignment 2', 'course': 'MATH 150 - Spring 2024'},
        {'name': 'Assignment 3', 'course': 'PHYS 201'},  # Current course
        {'name': 'Assignment 4', 'course': 'BIO 200 - Spring 2023'},  # Old
    ]
    
    print(f"\nFiltering for {current_semester} {current_year}:")
    filtered = filter_sys.filter_assignments_by_semester(
        test_assignments, current_semester, current_year)
    print(f"Kept {len(filtered)} assignments")
    
    return filtered


if __name__ == '__main__':
    test_semester_filter()