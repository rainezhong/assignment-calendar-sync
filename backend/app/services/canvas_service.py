"""
Canvas LMS API integration service.
Uses the official Canvas REST API to fetch courses and assignments.
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime
import asyncio


class CanvasService:
    """Service for interacting with Canvas LMS API."""

    def __init__(self, api_token: str, base_url: str):
        """
        Initialize Canvas service.

        Args:
            api_token: Canvas API access token
            base_url: Canvas instance URL (e.g., "umich.instructure.com")
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')

        # Ensure base_url has https://
        if not self.base_url.startswith('http'):
            self.base_url = f"https://{self.base_url}"

        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
        }

    async def test_connection(self) -> bool:
        """
        Test if the API token and base URL are valid.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/self",
                    headers=self.headers,
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Canvas connection test failed: {e}")
            return False

    async def get_current_user(self) -> Optional[Dict]:
        """
        Get current user information.

        Returns:
            User data dict or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/self",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching Canvas user: {e}")
            return None

    async def get_courses(self, enrollment_state: str = "active") -> List[Dict]:
        """
        Fetch all courses for the current user.

        Args:
            enrollment_state: Filter by enrollment state (active, completed, etc.)

        Returns:
            List of course dictionaries
        """
        try:
            courses = []
            page = 1
            per_page = 100

            async with httpx.AsyncClient() as client:
                while True:
                    response = await client.get(
                        f"{self.base_url}/api/v1/courses",
                        headers=self.headers,
                        params={
                            "enrollment_state": enrollment_state,
                            "per_page": per_page,
                            "page": page,
                            "include[]": ["term", "teachers"],
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()

                    page_courses = response.json()
                    if not page_courses:
                        break

                    courses.extend(page_courses)
                    page += 1

                    # Canvas returns empty array when no more pages
                    if len(page_courses) < per_page:
                        break

            return courses
        except Exception as e:
            print(f"Error fetching Canvas courses: {e}")
            return []

    async def get_assignments(self, course_id: int) -> List[Dict]:
        """
        Fetch all assignments for a specific course.

        Args:
            course_id: Canvas course ID

        Returns:
            List of assignment dictionaries
        """
        try:
            assignments = []
            page = 1
            per_page = 100

            async with httpx.AsyncClient() as client:
                while True:
                    response = await client.get(
                        f"{self.base_url}/api/v1/courses/{course_id}/assignments",
                        headers=self.headers,
                        params={
                            "per_page": per_page,
                            "page": page,
                            "include[]": ["submission"],
                        },
                        timeout=30.0,
                    )
                    response.raise_for_status()

                    page_assignments = response.json()
                    if not page_assignments:
                        break

                    assignments.extend(page_assignments)
                    page += 1

                    if len(page_assignments) < per_page:
                        break

            return assignments
        except Exception as e:
            print(f"Error fetching Canvas assignments for course {course_id}: {e}")
            return []

    async def get_all_assignments(self) -> Dict[int, List[Dict]]:
        """
        Fetch all assignments for all active courses.

        Returns:
            Dictionary mapping course_id to list of assignments
        """
        courses = await self.get_courses()
        all_assignments = {}

        # Fetch assignments for each course concurrently
        tasks = []
        for course in courses:
            course_id = course.get("id")
            if course_id:
                tasks.append(self._get_course_assignments(course_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for course, result in zip(courses, results):
            course_id = course.get("id")
            if isinstance(result, Exception):
                print(f"Error fetching assignments for course {course_id}: {result}")
                all_assignments[course_id] = []
            else:
                all_assignments[course_id] = result

        return all_assignments

    async def _get_course_assignments(self, course_id: int) -> List[Dict]:
        """Helper method for concurrent assignment fetching."""
        return await self.get_assignments(course_id)

    def parse_course(self, canvas_course: Dict) -> Dict:
        """
        Parse Canvas course data into our database format.

        Args:
            canvas_course: Raw Canvas course data

        Returns:
            Parsed course data for database
        """
        # Get instructor name from teachers array
        instructor = None
        if "teachers" in canvas_course and canvas_course["teachers"]:
            instructor = canvas_course["teachers"][0].get("display_name")

        # Get term/semester
        semester = None
        if "term" in canvas_course and canvas_course["term"]:
            semester = canvas_course["term"].get("name")

        return {
            "name": canvas_course.get("name", "Untitled Course"),
            "code": canvas_course.get("course_code"),
            "semester": semester,
            "instructor": instructor,
            "source": "canvas",
            "source_id": str(canvas_course.get("id")),
            "source_url": canvas_course.get("html_url"),
            "approved": False,  # Require user approval
        }

    def parse_assignment(self, canvas_assignment: Dict, course_id: int) -> Dict:
        """
        Parse Canvas assignment data into our database format.

        Args:
            canvas_assignment: Raw Canvas assignment data
            course_id: Database course ID (not Canvas ID)

        Returns:
            Parsed assignment data for database
        """
        # Parse due date
        due_date = canvas_assignment.get("due_at")
        if due_date:
            due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        else:
            # If no due date, set to far future
            due_date = datetime(2099, 12, 31)

        # Get submission data
        submission = canvas_assignment.get("submission", {}) or {}
        submission_status = None
        graded_at = None
        points_earned = None

        if submission:
            workflow_state = submission.get("workflow_state")
            submission_status = workflow_state  # submitted, graded, etc.

            if submission.get("graded_at"):
                graded_at = datetime.fromisoformat(
                    submission["graded_at"].replace("Z", "+00:00")
                )

            points_earned = submission.get("score")

        # Calculate grade percentage
        grade_percentage = None
        points_possible = canvas_assignment.get("points_possible")
        if points_earned is not None and points_possible and points_possible > 0:
            grade_percentage = (points_earned / points_possible) * 100

        return {
            "title": canvas_assignment.get("name", "Untitled Assignment"),
            "description": canvas_assignment.get("description"),
            "course_id": course_id,  # Our database course ID
            "assignment_type": self._map_assignment_type(
                canvas_assignment.get("submission_types", [])
            ),
            "due_date": due_date,
            "source": "canvas",
            "source_id": str(canvas_assignment.get("id")),
            "source_url": canvas_assignment.get("html_url"),
            "points_possible": points_possible,
            "points_earned": points_earned,
            "grade_percentage": grade_percentage,
            "submission_status": submission_status,
            "submission_url": canvas_assignment.get("html_url"),
            "graded_at": graded_at,
            "approved": False,  # Require user approval
        }

    def _map_assignment_type(self, submission_types: List[str]) -> str:
        """Map Canvas submission types to our assignment types."""
        if not submission_types:
            return "assignment"

        type_map = {
            "online_quiz": "exam",
            "discussion_topic": "discussion",
            "online_text_entry": "essay",
            "online_upload": "project",
            "external_tool": "project",
        }

        # Return first matching type
        for sub_type in submission_types:
            if sub_type in type_map:
                return type_map[sub_type]

        return "homework"
