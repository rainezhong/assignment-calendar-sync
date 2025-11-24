"""
Gradescope web scraping service using Playwright.
Since Gradescope has no public API, we use browser automation.
"""
from typing import List, Dict, Optional
from datetime import datetime
import re
import asyncio

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout


class GradescopeService:
    """Service for scraping Gradescope data with Playwright."""

    BASE_URL = "https://www.gradescope.com"

    def __init__(self, email: str, password: str):
        """
        Initialize Gradescope service.

        Args:
            email: Gradescope account email
            password: Gradescope account password
        """
        self.email = email
        self.password = password
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def initialize(self):
        """Launch browser and create context."""
        self.playwright = await async_playwright().start()

        # Launch headless browser with args for server environments
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
            ]
        )

        # Create browser context with realistic viewport
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        self.page = await self.context.new_page()

    async def close(self):
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def test_connection(self) -> bool:
        """
        Test if credentials are valid by attempting login.

        Returns:
            True if login successful, False otherwise
        """
        try:
            success = await self.login()
            return success
        except Exception as e:
            print(f"Gradescope connection test failed: {e}")
            return False

    async def login(self) -> bool:
        """
        Login to Gradescope.

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Navigate to login page
            await self.page.goto(f"{self.BASE_URL}/login", wait_until='networkidle', timeout=30000)

            # Fill in credentials
            await self.page.fill('input[name="email"]', self.email)
            await self.page.fill('input[name="password"]', self.password)

            # Click login button
            await self.page.click('button[type="submit"]')

            # Wait for navigation to complete
            await self.page.wait_for_load_state('networkidle', timeout=15000)

            # Check if login was successful by looking for account page or courses
            current_url = self.page.url

            if '/login' in current_url:
                # Still on login page - login failed
                return False

            if '/account' in current_url or '/courses' in current_url or current_url == f"{self.BASE_URL}/":
                return True

            # Try to find error message
            error_elements = await self.page.query_selector_all('.errorMsg, .alert-error, .error')
            if error_elements:
                return False

            # If we got here, assume success
            return True

        except PlaywrightTimeout:
            print("Login timeout - Gradescope may be slow or credentials invalid")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False

    async def get_courses(self) -> List[Dict]:
        """
        Scrape list of enrolled courses.

        Returns:
            List of course dictionaries
        """
        try:
            # Navigate to courses page (usually redirected here after login)
            await self.page.goto(f"{self.BASE_URL}/", wait_until='networkidle', timeout=30000)

            courses = []

            # Find all course boxes
            course_elements = await self.page.query_selector_all('.courseBox')

            for course_elem in course_elements:
                try:
                    # Extract course data
                    course_data = await self._parse_course_element(course_elem)
                    if course_data:
                        courses.append(course_data)
                except Exception as e:
                    print(f"Error parsing course: {e}")
                    continue

            return courses

        except Exception as e:
            print(f"Error fetching courses: {e}")
            return []

    async def _parse_course_element(self, element) -> Optional[Dict]:
        """Parse course data from course box element."""
        try:
            # Get course link to extract ID
            link_elem = await element.query_selector('a.courseBox--link')
            if not link_elem:
                return None

            course_url = await link_elem.get_attribute('href')
            if not course_url:
                return None

            # Extract course ID from URL (e.g., /courses/12345)
            match = re.search(r'/courses/(\d+)', course_url)
            if not match:
                return None

            course_id = match.group(1)

            # Get course shortname (e.g., "EECS 281")
            shortname_elem = await element.query_selector('.courseBox--shortname')
            shortname = await shortname_elem.text_content() if shortname_elem else "Unknown"

            # Get full course name
            name_elem = await element.query_selector('.courseBox--name')
            full_name = await name_elem.text_content() if name_elem else shortname

            # Get term (if available)
            # Term is usually in a parent element, try to find it
            term = None
            try:
                # Navigate up to find term heading
                parent = await element.evaluate_handle('el => el.closest(".courseList--term")')
                if parent:
                    term_elem = await parent.query_selector('.courseList--term-name')
                    if term_elem:
                        term = await term_elem.text_content()
            except Exception:
                pass

            return {
                'course_id': course_id,
                'shortname': shortname.strip(),
                'full_name': full_name.strip(),
                'term': term.strip() if term else None,
                'url': f"{self.BASE_URL}{course_url}",
            }

        except Exception as e:
            print(f"Error parsing course element: {e}")
            return None

    async def get_course_assignments(self, course_id: str) -> List[Dict]:
        """
        Scrape assignments for a specific course.

        Args:
            course_id: Gradescope course ID

        Returns:
            List of assignment dictionaries
        """
        try:
            # Navigate to course page
            course_url = f"{self.BASE_URL}/courses/{course_id}"
            await self.page.goto(course_url, wait_until='networkidle', timeout=30000)

            # Small delay to ensure dynamic content loads
            await asyncio.sleep(1)

            assignments = []

            # Find assignment table
            assignment_rows = await self.page.query_selector_all('table tbody tr')

            for row in assignment_rows:
                try:
                    assignment_data = await self._parse_assignment_element(row, course_id)
                    if assignment_data:
                        assignments.append(assignment_data)
                except Exception as e:
                    print(f"Error parsing assignment: {e}")
                    continue

            return assignments

        except Exception as e:
            print(f"Error fetching assignments for course {course_id}: {e}")
            return []

    async def _parse_assignment_element(self, row, course_id: str) -> Optional[Dict]:
        """Parse assignment data from table row."""
        try:
            # Get assignment link and name
            link_elem = await row.query_selector('a.table--primaryLink, th a')
            if not link_elem:
                return None

            assignment_name = await link_elem.text_content()
            assignment_url = await link_elem.get_attribute('href')

            if not assignment_name or not assignment_url:
                return None

            # Extract assignment ID from URL
            match = re.search(r'/assignments/(\d+)', assignment_url)
            assignment_id = match.group(1) if match else None

            # Get due date
            due_date = None
            due_date_elem = await row.query_selector('.submissionTimeChart--dueDate, .table--cell--primaryText')
            if due_date_elem:
                due_date_text = await due_date_elem.text_content()
                due_date = self._parse_due_date(due_date_text)

            # Get points/score
            points_possible = None
            points_earned = None
            grade_percentage = None

            score_elem = await row.query_selector('.assignment-score, .progressBar--percentage')
            if score_elem:
                score_text = await score_elem.text_content()
                points_earned, points_possible = self._parse_score(score_text)

                if points_earned is not None and points_possible and points_possible > 0:
                    grade_percentage = (points_earned / points_possible) * 100

            # Get submission status
            status_elem = await row.query_selector('.submissionStatus, .table--cell--secondaryText')
            submission_status = None
            if status_elem:
                status_text = await status_elem.text_content()
                submission_status = status_text.strip().lower()

            return {
                'assignment_id': assignment_id,
                'name': assignment_name.strip(),
                'course_id': course_id,
                'url': f"{self.BASE_URL}{assignment_url}" if assignment_url else None,
                'due_date': due_date,
                'points_possible': points_possible,
                'points_earned': points_earned,
                'grade_percentage': grade_percentage,
                'submission_status': submission_status,
            }

        except Exception as e:
            print(f"Error parsing assignment element: {e}")
            return None

    def _parse_due_date(self, date_text: str) -> Optional[datetime]:
        """Parse due date from text."""
        if not date_text:
            return None

        try:
            # Clean up text
            date_text = date_text.strip()

            # Common Gradescope formats:
            # "Nov 21, 2025 11:59 PM"
            # "November 21, 11:59 PM"
            # "11/21/2025 11:59 PM"

            from dateutil import parser

            # Try to parse with dateutil (handles many formats)
            parsed_date = parser.parse(date_text, fuzzy=True)
            return parsed_date

        except Exception as e:
            print(f"Could not parse date '{date_text}': {e}")
            return None

    def _parse_score(self, score_text: str) -> tuple[Optional[float], Optional[float]]:
        """
        Parse score text like "85 / 100" or "85.5/100".

        Returns:
            Tuple of (points_earned, points_possible)
        """
        if not score_text:
            return None, None

        try:
            # Match patterns like "85 / 100", "85.5/100", "85.5 / 100.0"
            match = re.search(r'([\d.]+)\s*/\s*([\d.]+)', score_text)
            if match:
                earned = float(match.group(1))
                possible = float(match.group(2))
                return earned, possible

            # Try just a single number (points earned, no total)
            match = re.search(r'([\d.]+)', score_text)
            if match:
                earned = float(match.group(1))
                return earned, None

        except Exception as e:
            print(f"Could not parse score '{score_text}': {e}")

        return None, None

    async def scrape_all_data(self) -> Dict:
        """
        Main orchestrator - scrape all courses and assignments.

        Returns:
            Dictionary with courses and assignments
        """
        courses = await self.get_courses()

        all_assignments = {}

        for course in courses:
            course_id = course['course_id']
            assignments = await self.get_course_assignments(course_id)
            all_assignments[course_id] = assignments

            # Small delay between courses to be respectful
            await asyncio.sleep(0.5)

        return {
            'courses': courses,
            'assignments': all_assignments,
        }

    def parse_course(self, course_data: Dict) -> Dict:
        """Parse course data into database format."""
        return {
            'name': course_data['full_name'],
            'code': course_data['shortname'],
            'semester': course_data.get('term'),
            'instructor': None,  # Gradescope doesn't show instructor on course list
            'source': 'gradescope',
            'source_id': course_data['course_id'],
            'source_url': course_data['url'],
            'approved': False,
        }

    def parse_assignment(self, assignment_data: Dict, db_course_id: int) -> Dict:
        """Parse assignment data into database format."""
        due_date = assignment_data['due_date']
        if not due_date:
            # Default to far future if no due date
            due_date = datetime(2099, 12, 31)

        return {
            'title': assignment_data['name'],
            'description': None,  # Would need to visit assignment page for description
            'course_id': db_course_id,
            'assignment_type': 'homework',  # Default, could be inferred from name
            'due_date': due_date,
            'source': 'gradescope',
            'source_id': assignment_data['assignment_id'],
            'source_url': assignment_data['url'],
            'points_possible': assignment_data.get('points_possible'),
            'points_earned': assignment_data.get('points_earned'),
            'grade_percentage': assignment_data.get('grade_percentage'),
            'submission_status': assignment_data.get('submission_status'),
            'approved': False,
        }
