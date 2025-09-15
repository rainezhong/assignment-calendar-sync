"""Assignment tracking and duplicate prevention system"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set
from utils import logger


class AssignmentTracker:
    """Tracks synced assignments and prevents duplicates"""
    
    def __init__(self):
        self.storage_file = Path.home() / '.assignment_sync_history.json'
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load existing tracking data"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    # Clean old entries (older than 6 months)
                    self.clean_old_entries(data)
                    return data
            except Exception as e:
                logger.warning(f"Could not load assignment history: {e}")
        
        return {
            'synced_assignments': {},
            'last_sync': None,
            'semesters': {}
        }
    
    def save_data(self):
        """Save tracking data to file"""
        try:
            self.data['last_sync'] = datetime.now().isoformat()
            with open(self.storage_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save assignment history: {e}")
    
    def clean_old_entries(self, data: Dict):
        """Remove entries older than 6 months"""
        cutoff = datetime.now() - timedelta(days=180)
        cutoff_str = cutoff.isoformat()
        
        # Clean synced assignments
        synced = data.get('synced_assignments', {})
        old_keys = [k for k, v in synced.items() 
                   if v.get('sync_date', '2020-01-01') < cutoff_str]
        for key in old_keys:
            del synced[key]
        
        logger.debug(f"Cleaned {len(old_keys)} old assignment entries")
    
    def generate_assignment_key(self, assignment: Dict) -> str:
        """Generate unique key for assignment"""
        # Create key from course + assignment name + due date
        course = assignment.get('course', 'unknown')
        name = assignment.get('name', 'unknown')
        due_date = assignment.get('due_date')
        due_str = due_date.strftime('%Y-%m-%d') if due_date else 'no-date'
        
        key_text = f"{course}|{name}|{due_str}"
        return hashlib.md5(key_text.encode()).hexdigest()[:16]
    
    def is_duplicate(self, assignment: Dict) -> bool:
        """Check if assignment has already been synced"""
        key = self.generate_assignment_key(assignment)
        return key in self.data['synced_assignments']
    
    def mark_as_synced(self, assignment: Dict):
        """Mark assignment as synced"""
        key = self.generate_assignment_key(assignment)
        self.data['synced_assignments'][key] = {
            'course': assignment.get('course'),
            'name': assignment.get('name'),
            'due_date': assignment.get('due_date').isoformat() if assignment.get('due_date') else None,
            'sync_date': datetime.now().isoformat(),
            'source': assignment.get('source', 'unknown')
        }
    
    def filter_new_assignments(self, assignments: List[Dict]) -> List[Dict]:
        """Filter out already synced assignments"""
        new_assignments = []
        duplicates = 0
        
        for assignment in assignments:
            if not self.is_duplicate(assignment):
                new_assignments.append(assignment)
            else:
                duplicates += 1
        
        logger.info(f"Filtered out {duplicates} duplicate assignments")
        return new_assignments
    
    def is_current_semester(self, assignment: Dict, course_name: str = None) -> bool:
        """Determine if assignment is from current/recent semester"""
        due_date = assignment.get('due_date')
        if not due_date:
            return False
        
        now = datetime.now()
        
        # Consider "current semester" as:
        # - Assignments due in the future
        # - Assignments due within the last 4 months (current semester)
        current_semester_start = now - timedelta(days=120)  # ~4 months ago
        future_cutoff = now + timedelta(days=180)  # ~6 months ahead
        
        # Assignment is current if it's between 4 months ago and 6 months ahead
        is_recent = current_semester_start <= due_date <= future_cutoff
        
        if is_recent:
            # Also check course patterns that suggest old semesters
            course_lower = course_name.lower() if course_name else assignment.get('course', '').lower()
            
            # Skip courses with old semester indicators
            old_indicators = [
                'sp2023', 'fa2023', 'spring 2023', 'fall 2023',
                'sp23', 'fa23', 'su23', 'summer 2023',
                'sp2022', 'fa2022', 'spring 2022', 'fall 2022',
                'sp22', 'fa22', 'su22', 'summer 2022'
            ]
            
            for indicator in old_indicators:
                if indicator in course_lower:
                    logger.debug(f"Filtering out old semester course: {course_name}")
                    return False
        
        return is_recent
    
    def filter_current_semester_assignments(self, assignments: List[Dict]) -> List[Dict]:
        """Filter assignments to only include current semester"""
        current_assignments = []
        old_count = 0
        
        for assignment in assignments:
            course = assignment.get('course', '')
            if self.is_current_semester(assignment, course):
                current_assignments.append(assignment)
            else:
                old_count += 1
                logger.debug(f"Filtered old assignment: {assignment.get('name')} from {course}")
        
        logger.info(f"Filtered out {old_count} assignments from old semesters")
        logger.info(f"Kept {len(current_assignments)} current semester assignments")
        
        return current_assignments
    
    def get_sync_summary(self) -> Dict:
        """Get summary of sync history"""
        total_synced = len(self.data['synced_assignments'])
        last_sync = self.data.get('last_sync')
        
        if last_sync:
            try:
                last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                last_sync_str = last_sync_dt.strftime('%Y-%m-%d %H:%M')
            except:
                last_sync_str = last_sync
        else:
            last_sync_str = "Never"
        
        return {
            'total_synced': total_synced,
            'last_sync': last_sync_str,
            'storage_file': str(self.storage_file)
        }


def test_assignment_tracker():
    """Test the assignment tracker"""
    print("Testing Assignment Tracker...")
    
    tracker = AssignmentTracker()
    
    # Test assignments
    test_assignments = [
        {
            'name': 'Current Assignment',
            'course': 'CS 101 - Fall 2024',
            'due_date': datetime.now() + timedelta(days=7),
            'source': 'test'
        },
        {
            'name': 'Old Assignment',
            'course': 'CS 200 - Spring 2023',
            'due_date': datetime.now() - timedelta(days=200),
            'source': 'test'
        },
        {
            'name': 'Future Assignment',
            'course': 'MATH 150',
            'due_date': datetime.now() + timedelta(days=30),
            'source': 'test'
        }
    ]
    
    print(f"Original assignments: {len(test_assignments)}")
    
    # Filter current semester
    current = tracker.filter_current_semester_assignments(test_assignments)
    print(f"Current semester assignments: {len(current)}")
    
    # Filter new assignments
    new = tracker.filter_new_assignments(current)
    print(f"New assignments (not duplicates): {len(new)}")
    
    # Mark as synced
    for assignment in new:
        tracker.mark_as_synced(assignment)
    
    tracker.save_data()
    
    print("Summary:", tracker.get_sync_summary())
    
    return new


if __name__ == '__main__':
    test_assignment_tracker()