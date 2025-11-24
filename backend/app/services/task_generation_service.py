"""
Task generation service using AI to break down assignments.
"""
import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import anthropic

from app.core.config import settings
from app.models.assignment import Assignment
from app.models.task import Task

logger = logging.getLogger(__name__)


class TaskGenerationService:
    """Generate actionable task breakdowns from assignments using AI."""

    def __init__(self):
        """Initialize with Anthropic client."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set - task generation will fail")
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_tasks_for_assignment(
        self,
        assignment: Assignment,
    ) -> List[Task]:
        """
        Generate a todo list breakdown for an assignment.

        Args:
            assignment: The assignment to break down

        Returns:
            List of Task objects (not yet saved to DB)
        """
        try:
            # Build prompt for AI
            prompt = self._build_task_generation_prompt(assignment)

            # Call AI
            response = await self._call_ai_api(prompt)

            # Parse structured response
            tasks_data = self._parse_ai_response(response)

            # Create Task objects
            tasks = []
            for i, task_data in enumerate(tasks_data):
                # Calculate due date for this task (spread across time until assignment due)
                task_due_date = self._calculate_task_due_date(
                    assignment.due_date,
                    i,
                    len(tasks_data)
                )

                task = Task(
                    assignment_id=assignment.id,
                    user_id=assignment.user_id,
                    title=task_data['title'],
                    description=task_data.get('description'),
                    priority=task_data.get('priority', 2),
                    order=i,
                    due_date=task_due_date,
                    is_completed=False,
                )
                tasks.append(task)

            logger.info(f"Generated {len(tasks)} tasks for assignment {assignment.id}")
            return tasks

        except Exception as e:
            logger.error(f"Failed to generate tasks for assignment {assignment.id}: {e}")
            # Return fallback tasks
            return self._generate_fallback_tasks(assignment)

    def _build_task_generation_prompt(self, assignment: Assignment) -> str:
        """Build AI prompt with assignment context."""
        days_until_due = (assignment.due_date - datetime.utcnow()).days

        return f"""You are a task breakdown assistant helping students manage their coursework.

Given the following assignment, break it down into 5-8 specific, actionable tasks:

**Assignment Details:**
- Title: {assignment.title}
- Course: {assignment.course_name}
- Type: {assignment.assignment_type}
- Description: {assignment.description or "No description provided"}
- Due Date: {assignment.due_date.strftime('%B %d, %Y')} ({days_until_due} days from now)
- Estimated Hours: {assignment.estimated_hours or "Unknown"}

**Instructions:**
1. Break down this assignment into 5-8 concrete, actionable tasks
2. Order tasks logically (setup → work → submission)
3. Assign priority: 1 (high/urgent), 2 (medium), 3 (low)
4. Make tasks specific and achievable
5. Include a final submission task

**Output Format (JSON only, no other text):**
{{
  "tasks": [
    {{
      "title": "Review assignment requirements and rubric",
      "description": "Read through all instructions to understand expectations",
      "priority": 1
    }},
    {{
      "title": "Research and gather materials",
      "description": "Find relevant sources and resources needed",
      "priority": 1
    }},
    {{
      "title": "Complete main work",
      "description": "Work on the core assignment deliverables",
      "priority": 1
    }},
    {{
      "title": "Review and revise",
      "description": "Check work for errors and completeness",
      "priority": 2
    }},
    {{
      "title": "Submit assignment",
      "description": "Upload to Canvas before deadline",
      "priority": 1
    }}
  ]
}}

Generate realistic tasks that will help the student make steady progress. Return only valid JSON."""

    async def _call_ai_api(self, prompt: str) -> str:
        """Call Claude API."""
        message = await self.client.messages.create(
            model="claude-3-5-haiku-20241022",  # Using Haiku for speed and cost
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def _parse_ai_response(self, response: str) -> List[Dict]:
        """Parse AI response into structured task data."""
        # Extract JSON from response
        json_str = response.strip()

        # Handle cases where AI wraps JSON in markdown code blocks
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(json_str)
            tasks = data.get('tasks', [])

            # Validate tasks
            if not isinstance(tasks, list) or len(tasks) == 0:
                raise ValueError("No tasks found in response")

            # Ensure required fields
            for task in tasks:
                if 'title' not in task:
                    raise ValueError("Task missing title field")
                if 'priority' not in task:
                    task['priority'] = 2  # Default to medium priority

            return tasks

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response was: {response}")
            raise

    def _calculate_task_due_date(
        self,
        assignment_due_date: datetime,
        task_index: int,
        total_tasks: int
    ) -> datetime:
        """
        Calculate when a task should be due.
        Distributes tasks evenly from now until assignment due date.
        """
        now = datetime.utcnow().replace(tzinfo=assignment_due_date.tzinfo)
        time_available = assignment_due_date - now

        if time_available.total_seconds() <= 0:
            # Assignment already due, all tasks due immediately
            return assignment_due_date

        # Distribute tasks across available time
        # Last task due at assignment due date
        # Earlier tasks due proportionally earlier
        if task_index == total_tasks - 1:
            # Last task (usually submission) due at assignment deadline
            return assignment_due_date
        else:
            # Distribute other tasks evenly
            portion = (task_index + 1) / total_tasks
            task_due = now + timedelta(seconds=time_available.total_seconds() * portion)
            return task_due

    def _generate_fallback_tasks(self, assignment: Assignment) -> List[Task]:
        """
        Generate simple fallback tasks if AI fails.
        """
        logger.info(f"Generating fallback tasks for assignment {assignment.id}")

        fallback_tasks_data = [
            {
                "title": "Review assignment requirements",
                "description": "Read through all instructions and rubric",
                "priority": 1,
            },
            {
                "title": "Plan approach and gather materials",
                "description": "Outline strategy and collect needed resources",
                "priority": 1,
            },
            {
                "title": f"Complete {assignment.assignment_type}",
                "description": "Work on the main assignment deliverables",
                "priority": 1,
            },
            {
                "title": "Review and revise work",
                "description": "Check for completeness and quality",
                "priority": 2,
            },
            {
                "title": "Submit assignment",
                "description": f"Submit on {assignment.source} before deadline",
                "priority": 1,
            }
        ]

        tasks = []
        for i, task_data in enumerate(fallback_tasks_data):
            task_due_date = self._calculate_task_due_date(
                assignment.due_date,
                i,
                len(fallback_tasks_data)
            )

            task = Task(
                assignment_id=assignment.id,
                user_id=assignment.user_id,
                title=task_data['title'],
                description=task_data['description'],
                priority=task_data['priority'],
                order=i,
                due_date=task_due_date,
                is_completed=False,
            )
            tasks.append(task)

        return tasks
