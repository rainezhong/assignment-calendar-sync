#!/usr/bin/env python3
"""Analyze course ID patterns and assignment dates to infer semesters"""

# From your sync output, let's analyze the patterns:

course_data = {
    "1104572": {
        "name": "CS 61C", 
        "assignments": [
            "2025-09-02"  # Lab 0
        ]
    },
    "1104536": {
        "name": "CS 61B",
        "assignments": [
            "2025-09-01",  # Mini-Vitamin 0B
            "2025-08-30"   # Homework 0
        ]
    },
    "961758": {
        "name": "CS 61B",
        "assignments": [
            "2025-05-04",  # Homework 4: Final Exam Review
            "2025-03-21",  # Project 2B: Checkpoint
            "2025-03-07",  # Homework 2
            "2025-04-04",  # Homework 3
            "2025-01-24",  # Homework 0A
            "2025-02-10",  # Project 1A
            "2025-04-07",  # Project 2B: Wordnet
            "2025-03-12"   # Project 2A: Ngrams
        ]
    },
    "963410": {
        "name": "EECS 16A",
        "assignments": [
            "2025-05-08",  # Design Project Slides
            "2025-05-07",  # HW10
            "2025-04-27",  # HW8_selfgrading, Design Project: Checkpoint 2
            "2025-04-25",  # Design Project: Checkpoint 1, HW9
            "2025-04-18",  # HW8
            "2025-03-28",  # HW6
            "2025-03-14",  # HW5
            "2025-02-28",  # HW4
            "2025-02-21",  # HW3
            "2025-02-14",  # HW2
            "2025-02-07"   # HW1
        ]
    },
    "843175": {
        "name": "CS 61A",
        "assignments": [
            "2025-12-22",  # Discussion Attendance
            "2025-12-05",  # Homework 10
            "2025-12-02",  # Homework 9
            "2025-11-26",  # Scheme
            "2025-11-14",  # Homework 8
            "2025-10-24",  # Homework 6
            "2025-10-17",  # Homework 5
            "2025-10-10",  # Homework 4
            "2025-09-26",  # Homework 3
            "2025-09-12",  # Homework 2
            "2025-09-09",  # Homework 1
            "2025-09-04"   # Lab 1, Lab 0
        ]
    },
    "823368": {
        "name": "EECS 16B", 
        "assignments": [
            "2025-12-23",  # Lab Checkoffs
            "2025-12-11",  # Extra Credit
            "2025-11-24",  # HW12
            "2025-11-17",  # HW11
            "2025-11-10",  # HW10
            "2025-11-03",  # HW9
            "2025-10-27",  # HW8
            "2025-10-20",  # HW7
            "2025-10-13",  # HW6
            "2025-10-06",  # HW5
            "2025-09-29",  # HW4
            "2025-09-22",  # HW3
            "2025-09-15",  # HW2
            "2025-09-08",  # HW1
            "2025-09-01"   # HW0
        ]
    },
    "844232": {
        "name": "MATH 53-LEC-001",
        "assignments": [
            "2025-11-04"   # Essay 1, Essay 2
        ]
    },
    "850761": {
        "name": "Math 53 Section 104 106",
        "assignments": [
            "2025-12-02",  # HW 13
            "2025-11-18",  # HW 12
            "2025-11-04",  # HW 10
            "2025-10-28",  # HW 9
            "2025-09-30",  # HW 5
            "2025-09-23",  # HW 4
            "2025-09-16",  # HW 3
            "2025-09-09",  # HW 2
            "2025-09-03"   # HW 1
        ]
    }
}

def analyze_semester_patterns():
    print("🔍 ANALYZING COURSE ID AND DATE PATTERNS")
    print("="*60)
    
    # Group courses by assignment date patterns
    spring_courses = []  # Jan-May assignments
    fall_courses = []    # Sep-Dec assignments
    summer_courses = []  # Jun-Aug assignments
    mixed_courses = []   # Multiple semesters
    
    for course_id, data in course_data.items():
        name = data['name']
        assignments = data['assignments']
        
        # Analyze assignment months
        months = []
        for date_str in assignments:
            month = int(date_str.split('-')[1])
            months.append(month)
        
        # Determine semester pattern
        spring_months = [m for m in months if 1 <= m <= 5]
        summer_months = [m for m in months if 6 <= m <= 8] 
        fall_months = [m for m in months if 9 <= m <= 12]
        
        total_assignments = len(assignments)
        
        print(f"\n📚 Course {course_id} ({name}):")
        print(f"   📊 {total_assignments} assignments")
        print(f"   📅 Months: {sorted(set(months))}")
        
        if spring_months and not fall_months and not summer_months:
            spring_courses.append((course_id, name))
            print(f"   🌸 SPRING SEMESTER (Jan-May only)")
        elif fall_months and not spring_months and not summer_months:
            fall_courses.append((course_id, name))
            print(f"   🍂 FALL SEMESTER (Sep-Dec only)")
        elif summer_months and not spring_months and not fall_months:
            summer_courses.append((course_id, name))
            print(f"   ☀️ SUMMER SEMESTER (Jun-Aug only)")
        else:
            mixed_courses.append((course_id, name))
            if spring_months and fall_months:
                print(f"   🔄 MIXED SEMESTER (spans Spring & Fall)")
            elif len(set(months)) > 6:
                print(f"   📆 FULL YEAR COURSE")
            else:
                print(f"   ❓ UNCLEAR PATTERN")
    
    print(f"\n{'='*60}")
    print("📊 SEMESTER CLASSIFICATION SUMMARY")
    print(f"{'='*60}")
    
    print(f"\n🌸 SPRING COURSES ({len(spring_courses)}):")
    for course_id, name in spring_courses:
        print(f"   {course_id}: {name}")
    
    print(f"\n🍂 FALL COURSES ({len(fall_courses)}):")
    for course_id, name in fall_courses:
        print(f"   {course_id}: {name}")
    
    print(f"\n☀️ SUMMER COURSES ({len(summer_courses)}):")
    for course_id, name in summer_courses:
        print(f"   {course_id}: {name}")
    
    print(f"\n🔄 MIXED/UNCLEAR COURSES ({len(mixed_courses)}):")
    for course_id, name in mixed_courses:
        print(f"   {course_id}: {name}")
    
    # Analyze course ID patterns
    print(f"\n{'='*60}")
    print("🔢 COURSE ID PATTERN ANALYSIS")
    print(f"{'='*60}")
    
    all_ids = [int(course_id) for course_id in course_data.keys()]
    all_ids.sort()
    
    print(f"Course ID range: {min(all_ids)} - {max(all_ids)}")
    print(f"ID progression:")
    for course_id in all_ids:
        name = course_data[str(course_id)]['name']
        semester_type = "Unknown"
        
        if (str(course_id), name) in spring_courses:
            semester_type = "Spring"
        elif (str(course_id), name) in fall_courses:
            semester_type = "Fall"
        elif (str(course_id), name) in mixed_courses:
            semester_type = "Mixed"
            
        print(f"   {course_id}: {name} ({semester_type})")

if __name__ == '__main__':
    analyze_semester_patterns()