#!/usr/bin/env python3
"""Test the ICS generator with sample assignments"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path('python')))

from ics_generator import ICSGenerator

# Create sample assignments
sample_assignments = [
    {
        'name': 'Calculus Problem Set 3',
        'course': 'MATH 101 - Calculus I',
        'due_date': datetime.now() + timedelta(days=3, hours=10),
        'url': 'https://gradescope.com/assignments/123',
        'points': 50,
        'source': 'gradescope'
    },
    {
        'name': 'Essay on Climate Change',
        'course': 'ENGL 102 - Composition',
        'due_date': datetime.now() + timedelta(days=7, hours=23, minutes=59),
        'url': 'https://canvas.school.edu/assignments/456',
        'source': 'canvas'
    },
    {
        'name': 'Physics Lab Report 2',
        'course': 'PHYS 201 - General Physics',
        'due_date': datetime.now() + timedelta(days=5, hours=15, minutes=30),
        'url': 'https://gradescope.com/assignments/789',
        'points': 25,
        'source': 'gradescope'
    }
]

def test_ics_generation():
    print("Testing ICS file generation...")
    
    generator = ICSGenerator()
    
    # Add assignments
    for assignment in sample_assignments:
        generator.add_assignment(assignment)
    
    # Generate ICS file
    filename = 'test_assignments.ics'
    content = generator.generate_ics(filename)
    
    print(f"✅ Generated {filename}")
    print(f"File size: {len(content)} characters")
    
    # Show preview
    lines = content.split('\n')
    print(f"\nFirst 20 lines of generated ICS file:")
    print("-" * 50)
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:2}: {line}")
    print("...")
    
    return filename

if __name__ == '__main__':
    test_ics_generation()