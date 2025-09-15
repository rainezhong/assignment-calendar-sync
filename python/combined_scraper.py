"""Gradescope scraper with SSO support"""

from typing import List, Dict
import config
from utils import logger
from scraper import GradescopeScraper


class GradescopeAssignmentFetcher:
    """Fetches assignments from Gradescope via scraping"""
    
    def __init__(self):
        self.gradescope_scraper = None
        self.all_assignments = []
        
        # Initialize Gradescope scraper
        self.gradescope_scraper = GradescopeScraper()
    
    def fetch_all_assignments(self) -> List[Dict]:
        """Fetch assignments from Gradescope"""
        all_assignments = []
        
        # Fetch from Gradescope
        try:
            logger.info("Fetching assignments from Gradescope...")
            gradescope_assignments = self.gradescope_scraper.get_assignments()
            
            # Add source field
            for assignment in gradescope_assignments:
                assignment['source'] = 'gradescope'
            
            all_assignments.extend(gradescope_assignments)
            logger.success(f"Retrieved {len(gradescope_assignments)} assignments from Gradescope")
        except Exception as e:
            logger.error(f"Failed to fetch Gradescope assignments: {e}")
        finally:
            self.gradescope_scraper.cleanup()
        
        logger.info(f"Total assignments: {len(all_assignments)}")
        self.all_assignments = all_assignments
        return all_assignments
    
    def print_summary(self):
        """Print a summary of fetched assignments"""
        if not self.all_assignments:
            print("No assignments found")
            return
        
        print("\n" + "=" * 60)
        print("ASSIGNMENT SUMMARY")
        print("=" * 60)
        
        # Group by source
        by_source = {}
        for assignment in self.all_assignments:
            source = assignment.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(assignment)
        
        # Print by source
        for source, source_assignments in by_source.items():
            print(f"\n📱 From {source.capitalize()}:")
            
            # Group by course
            by_course = {}
            for assignment in source_assignments:
                course = assignment['course']
                if course not in by_course:
                    by_course[course] = []
                by_course[course].append(assignment)
            
            for course, course_assignments in by_course.items():
                print(f"\n  📚 {course}:")
                for assignment in course_assignments:
                    if assignment['due_date']:
                        print(f"    ✓ {assignment['name']} - Due: {assignment['due_date'].strftime('%Y-%m-%d %H:%M')}")
                    else:
                        print(f"    • {assignment['name']} - No due date")
        
        print("\n" + "=" * 60)


def test_gradescope_fetcher():
    """Test the Gradescope assignment fetcher"""
    print("\n" + "=" * 50)
    print("Testing Gradescope Assignment Fetcher")
    print("=" * 50)
    
    fetcher = GradescopeAssignmentFetcher()
    assignments = fetcher.fetch_all_assignments()
    fetcher.print_summary()
    
    return assignments


if __name__ == '__main__':
    test_gradescope_fetcher()