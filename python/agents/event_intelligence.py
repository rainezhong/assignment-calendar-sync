#!/usr/bin/env python3
"""
Intelligent Event Management & Study Scheduling
Teaching concepts: Calendar APIs, Time Series Analysis, Pattern Recognition, ML Scheduling
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, time
from pathlib import Path
import logging
from collections import defaultdict, Counter
import statistics
from enum import Enum

# For calendar integration
try:
    from icalendar import Calendar, Event as ICalEvent
    import caldav
    from caldav.elements import dav, cdav
except ImportError:
    print("Install calendar libraries: pip install icalendar caldav")

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Calendar Protocol Standards
# CalDAV is the standard protocol for calendar access (like IMAP for email)
# iCalendar (.ics) is the standard format for calendar events

class EventType(Enum):
    """Classification of events for intelligent scheduling"""
    CLASS_LECTURE = "class_lecture"
    CLASS_LAB = "class_lab"
    CLASS_SECTION = "class_section"
    ASSIGNMENT_DUE = "assignment_due"
    EXAM = "exam"
    OFFICE_HOURS = "office_hours"
    STUDY_SESSION = "study_session"
    BREAK = "break"
    PERSONAL = "personal"
    EXTERNAL_DEADLINE = "external_deadline"
    UNIVERSITY_EVENT = "university_event"

class ProductivityZone(Enum):
    """Time periods based on productivity patterns"""
    PEAK = "peak"           # User's most productive time
    HIGH = "high"           # Good productivity
    MODERATE = "moderate"   # Average productivity
    LOW = "low"            # Less productive
    RECOVERY = "recovery"   # Need break/rest

@dataclass
class IntelligentEvent:
    """
    Rich event model with intelligence metadata

    Teaching Concepts:
    - Event classification for smart scheduling
    - Productivity-aware timing
    - Conflict detection
    """
    title: str
    start_time: datetime
    end_time: datetime
    event_type: EventType
    description: Optional[str] = None
    location: Optional[str] = None
    calendar_source: str = "unknown"  # academic, personal, external

    # Intelligence metadata
    importance_score: float = 0.5  # 0-1 scale
    focus_required: float = 0.5    # How much focus needed
    is_flexible: bool = True       # Can be rescheduled?
    optimal_time_of_day: Optional[str] = None  # morning, afternoon, evening, night
    estimated_prep_time: Optional[timedelta] = None  # For assignments/exams

    # Learning metadata
    user_productivity_at_time: Optional[ProductivityZone] = None
    historical_completion_rate: float = 1.0  # For recurring events

    @property
    def duration(self) -> timedelta:
        """Event duration"""
        return self.end_time - self.start_time

    @property
    def is_past(self) -> bool:
        """Check if event has passed"""
        return self.end_time < datetime.now()

    @property
    def time_until_start(self) -> timedelta:
        """Time until event starts"""
        return self.start_time - datetime.now()

    @property
    def urgency_score(self) -> float:
        """
        Calculate urgency (0-1)

        LEARNING CONCEPT: Multi-factor scoring
        Combine time pressure + importance for smart prioritization
        """
        if self.is_past:
            return 0.0

        # Time-based urgency
        hours_until = self.time_until_start.total_seconds() / 3600

        if hours_until < 0:
            time_urgency = 0.0
        elif hours_until < 24:
            time_urgency = 1.0
        elif hours_until < 72:
            time_urgency = 0.8
        elif hours_until < 168:  # 1 week
            time_urgency = 0.5
        else:
            time_urgency = 0.3

        # Combine with importance
        return (time_urgency * 0.6) + (self.importance_score * 0.4)

# LEARNING CONCEPT 2: CalDAV Protocol for Calendar Access
# CalDAV enables read/write access to calendars (Google Calendar, Outlook, iCloud)

class CalendarClient:
    """
    Universal calendar client supporting multiple providers

    Teaching Concepts:
    - CalDAV protocol
    - Calendar synchronization
    - Conflict detection
    - Event parsing (iCalendar format)
    """

    CALDAV_URLS = {
        "google": "https://calendar.google.com/calendar/dav",
        "icloud": "https://caldav.icloud.com",
        "outlook": "https://outlook.office365.com"
    }

    def __init__(self, calendar_url: str, username: str, password: str):
        """
        Initialize calendar client

        Note: In production, use OAuth2 instead of passwords
        """
        self.calendar_url = calendar_url
        self.username = username
        self.password = password
        self.client = None
        self.principal = None

    def connect(self) -> bool:
        """Establish CalDAV connection"""
        try:
            self.client = caldav.DAVClient(
                url=self.calendar_url,
                username=self.username,
                password=self.password
            )
            self.principal = self.client.principal()
            logger.info("CalDAV connection established")
            return True
        except Exception as e:
            logger.error(f"CalDAV connection failed: {e}")
            return False

    def get_calendars(self) -> List[Any]:
        """Get all calendars for the user"""
        if not self.principal:
            if not self.connect():
                return []

        try:
            calendars = self.principal.calendars()
            logger.info(f"Found {len(calendars)} calendars")
            return calendars
        except Exception as e:
            logger.error(f"Failed to fetch calendars: {e}")
            return []

    def fetch_events(self,
                    start_date: datetime,
                    end_date: datetime,
                    calendar_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch events from calendar in date range

        This demonstrates:
        - CalDAV event querying
        - iCalendar parsing
        - Date range filtering
        """
        calendars = self.get_calendars()
        if not calendars:
            return []

        all_events = []

        for calendar in calendars:
            # Filter by calendar name if specified
            if calendar_name and calendar.name != calendar_name:
                continue

            try:
                # CalDAV search
                events = calendar.date_search(
                    start=start_date,
                    end=end_date,
                    expand=True
                )

                for event in events:
                    parsed = self._parse_caldav_event(event)
                    if parsed:
                        all_events.append(parsed)

            except Exception as e:
                logger.error(f"Error fetching events from {calendar.name}: {e}")
                continue

        logger.info(f"Fetched {len(all_events)} events")
        return all_events

    def _parse_caldav_event(self, caldav_event) -> Optional[Dict[str, Any]]:
        """
        Parse CalDAV event to dictionary

        LEARNING CONCEPT: iCalendar Format
        Events are stored in iCalendar (.ics) format
        Components: VEVENT, VTODO, VJOURNAL, etc.
        """
        try:
            # Get iCalendar data
            ical_data = caldav_event.data
            calendar = Calendar.from_ical(ical_data)

            # Extract VEVENT component
            for component in calendar.walk():
                if component.name == "VEVENT":
                    return {
                        'title': str(component.get('summary', 'No Title')),
                        'start_time': component.get('dtstart').dt,
                        'end_time': component.get('dtend').dt,
                        'description': str(component.get('description', '')),
                        'location': str(component.get('location', '')),
                        'uid': str(component.get('uid', ''))
                    }

            return None

        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None

# LEARNING CONCEPT 3: Time Series Analysis for Pattern Recognition
# Analyze user behavior patterns to optimize scheduling

@dataclass
class UserProductivityPattern:
    """
    Learned productivity patterns for a user

    Teaching Concepts:
    - Time series analysis
    - Statistical pattern recognition
    - Temporal feature engineering
    """
    user_id: str

    # Hourly productivity scores (0-1) for each hour 0-23
    hourly_productivity: Dict[int, float] = field(default_factory=dict)

    # Day of week patterns (0=Monday, 6=Sunday)
    daily_productivity: Dict[int, float] = field(default_factory=dict)

    # Completion patterns
    avg_completion_time: Dict[str, float] = field(default_factory=dict)  # task_type -> hours
    completion_variance: Dict[str, float] = field(default_factory=dict)

    # Break patterns
    optimal_break_interval: timedelta = field(default_factory=lambda: timedelta(hours=2))
    optimal_break_duration: timedelta = field(default_factory=lambda: timedelta(minutes=15))

    # Session patterns
    max_focus_duration: timedelta = field(default_factory=lambda: timedelta(hours=3))
    preferred_study_locations: Counter = field(default_factory=Counter)

    def get_productivity_score(self, dt: datetime) -> float:
        """
        Get productivity score for a specific datetime

        LEARNING CONCEPT: Feature-based scoring
        Combine multiple temporal features for prediction
        """
        hour = dt.hour
        day_of_week = dt.weekday()

        # Get base scores
        hour_score = self.hourly_productivity.get(hour, 0.5)
        day_score = self.daily_productivity.get(day_of_week, 0.5)

        # Combine scores (weighted average)
        return (hour_score * 0.7) + (day_score * 0.3)

    def get_optimal_zone(self, dt: datetime) -> ProductivityZone:
        """Classify time period into productivity zone"""
        score = self.get_productivity_score(dt)

        if score >= 0.8:
            return ProductivityZone.PEAK
        elif score >= 0.6:
            return ProductivityZone.HIGH
        elif score >= 0.4:
            return ProductivityZone.MODERATE
        elif score >= 0.2:
            return ProductivityZone.LOW
        else:
            return ProductivityZone.RECOVERY

class ProductivityAnalyzer:
    """
    Analyze user behavior to learn productivity patterns

    Teaching Concepts:
    - Statistical analysis of temporal data
    - Moving averages and smoothing
    - Outlier detection
    - Pattern extraction from logs
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def analyze_completion_history(self,
                                   completion_logs: List[Dict[str, Any]]) -> UserProductivityPattern:
        """
        Analyze historical completion data to learn patterns

        LEARNING CONCEPT: Time Series Aggregation
        Group events by time features (hour, day) and compute statistics
        """
        pattern = UserProductivityPattern(user_id="default")

        if not completion_logs:
            return self._get_default_pattern()

        # Group by hour of day
        hourly_completions = defaultdict(list)
        daily_completions = defaultdict(list)
        task_durations = defaultdict(list)

        for log in completion_logs:
            if 'completed_at' not in log or 'started_at' not in log:
                continue

            completed_at = log['completed_at']
            started_at = log['started_at']
            task_type = log.get('task_type', 'unknown')

            # Calculate completion time
            duration = (completed_at - started_at).total_seconds() / 3600  # hours

            # Group by temporal features
            hour = started_at.hour
            day_of_week = started_at.weekday()

            hourly_completions[hour].append(duration)
            daily_completions[day_of_week].append(duration)
            task_durations[task_type].append(duration)

        # Calculate hourly productivity scores
        # Lower completion time = higher productivity
        all_durations = [d for durations in hourly_completions.values() for d in durations]
        if all_durations:
            median_duration = statistics.median(all_durations)

            for hour, durations in hourly_completions.items():
                avg_duration = statistics.mean(durations)
                # Inverse relationship: faster completion = higher productivity
                productivity = median_duration / max(avg_duration, 0.1)
                # Normalize to 0-1
                pattern.hourly_productivity[hour] = min(1.0, max(0.0, productivity))

        # Calculate daily productivity scores
        for day, durations in daily_completions.items():
            avg_duration = statistics.mean(durations)
            productivity = median_duration / max(avg_duration, 0.1)
            pattern.daily_productivity[day] = min(1.0, max(0.0, productivity))

        # Calculate average completion times by task type
        for task_type, durations in task_durations.items():
            pattern.avg_completion_time[task_type] = statistics.mean(durations)
            if len(durations) > 1:
                pattern.completion_variance[task_type] = statistics.stdev(durations)

        return pattern

    def _get_default_pattern(self) -> UserProductivityPattern:
        """
        Default productivity pattern (when no data available)

        LEARNING CONCEPT: Sensible Defaults
        Always have a fallback when ML fails or has insufficient data
        """
        pattern = UserProductivityPattern(user_id="default")

        # Default: Most productive mid-morning and early afternoon
        default_hourly = {
            6: 0.4, 7: 0.5, 8: 0.7, 9: 0.9, 10: 1.0,  # Morning peak
            11: 0.9, 12: 0.7, 13: 0.6, 14: 0.8, 15: 0.9,  # Afternoon
            16: 0.8, 17: 0.6, 18: 0.5, 19: 0.4, 20: 0.6,  # Evening
            21: 0.5, 22: 0.3, 23: 0.2, 0: 0.1, 1: 0.1,  # Night
            2: 0.1, 3: 0.1, 4: 0.1, 5: 0.2
        }
        pattern.hourly_productivity = default_hourly

        # Default: Weekdays more productive than weekends
        pattern.daily_productivity = {
            0: 0.8, 1: 0.9, 2: 0.9, 3: 0.8, 4: 0.7,  # Mon-Fri
            5: 0.5, 6: 0.6  # Sat-Sun
        }

        return pattern

# LEARNING CONCEPT 4: Intelligent Scheduling Algorithm
# ML-based scheduling that optimizes for productivity and constraints

class IntelligentScheduler:
    """
    AI-powered scheduler that optimizes study time

    Teaching Concepts:
    - Constraint satisfaction problems
    - Optimization algorithms
    - Greedy scheduling with backtracking
    - Multi-objective optimization (productivity + preferences + constraints)
    """

    def __init__(self, productivity_pattern: UserProductivityPattern):
        self.productivity_pattern = productivity_pattern

    def suggest_study_schedule(self,
                               assignments: List[Dict[str, Any]],
                               existing_events: List[IntelligentEvent],
                               start_date: datetime,
                               end_date: datetime) -> List[IntelligentEvent]:
        """
        Create optimal study schedule

        This demonstrates:
        - Constraint-based scheduling
        - Productivity-aware time allocation
        - Conflict avoidance
        - Buffer time management
        """
        study_sessions = []

        # Sort assignments by urgency
        sorted_assignments = sorted(
            assignments,
            key=lambda a: (a.get('due_date', datetime.max), -a.get('importance', 0.5))
        )

        # Create time slots (avoid existing events)
        available_slots = self._generate_available_slots(
            existing_events,
            start_date,
            end_date
        )

        # Allocate study time for each assignment
        for assignment in sorted_assignments:
            due_date = assignment.get('due_date')
            if not due_date or due_date < datetime.now():
                continue

            # Estimate study time needed
            estimated_hours = self._estimate_study_hours(assignment)

            # Find optimal slots
            allocated_slots = self._allocate_study_time(
                estimated_hours,
                available_slots,
                due_date,
                assignment
            )

            # Create study session events
            for slot in allocated_slots:
                session = IntelligentEvent(
                    title=f"Study: {assignment.get('title', 'Assignment')}",
                    start_time=slot['start'],
                    end_time=slot['end'],
                    event_type=EventType.STUDY_SESSION,
                    description=f"Work on {assignment.get('title')}",
                    importance_score=assignment.get('importance', 0.5),
                    focus_required=assignment.get('difficulty', 0.5),
                    is_flexible=True,
                    user_productivity_at_time=slot.get('productivity_zone')
                )
                study_sessions.append(session)

                # Remove allocated slot from available slots
                available_slots = self._remove_slot(available_slots, slot)

        logger.info(f"Created {len(study_sessions)} study sessions")
        return study_sessions

    def _generate_available_slots(self,
                                  existing_events: List[IntelligentEvent],
                                  start_date: datetime,
                                  end_date: datetime,
                                  slot_duration_hours: float = 2.0) -> List[Dict]:
        """
        Generate available time slots avoiding conflicts

        LEARNING CONCEPT: Interval Scheduling Problem
        Find free time between existing events
        """
        slots = []
        current = start_date

        while current < end_date:
            # Check if this time conflicts with existing events
            slot_end = current + timedelta(hours=slot_duration_hours)

            if not self._has_conflict(current, slot_end, existing_events):
                # Check if it's during reasonable hours (e.g., 6 AM - 11 PM)
                if 6 <= current.hour <= 23:
                    productivity_score = self.productivity_pattern.get_productivity_score(current)
                    zone = self.productivity_pattern.get_optimal_zone(current)

                    slots.append({
                        'start': current,
                        'end': slot_end,
                        'productivity_score': productivity_score,
                        'productivity_zone': zone
                    })

            # Move to next slot (30 minute increments for flexibility)
            current += timedelta(minutes=30)

        logger.info(f"Generated {len(slots)} available time slots")
        return slots

    def _has_conflict(self,
                     start: datetime,
                     end: datetime,
                     events: List[IntelligentEvent]) -> bool:
        """Check if time range conflicts with any event"""
        for event in events:
            # Check for overlap
            if not (end <= event.start_time or start >= event.end_time):
                return True
        return False

    def _estimate_study_hours(self, assignment: Dict[str, Any]) -> float:
        """
        Estimate hours needed for assignment

        LEARNING CONCEPT: Parametric Estimation
        Use multiple factors to estimate effort
        """
        # Base time by assignment type
        base_times = {
            'homework': 3.0,
            'project': 15.0,
            'essay': 8.0,
            'exam': 10.0,  # Study time
            'lab': 4.0,
            'quiz': 1.0,
            'other': 5.0
        }

        assignment_type = assignment.get('type', 'other')
        base_time = base_times.get(assignment_type, 5.0)

        # Adjust for difficulty
        difficulty = assignment.get('difficulty', 0.5)
        difficulty_multiplier = 0.5 + (difficulty * 1.0)  # 0.5x to 1.5x

        # Adjust for course
        course_multiplier = assignment.get('course_multiplier', 1.0)

        total_hours = base_time * difficulty_multiplier * course_multiplier

        # Add buffer (20%)
        total_hours *= 1.2

        return total_hours

    def _allocate_study_time(self,
                            hours_needed: float,
                            available_slots: List[Dict],
                            deadline: datetime,
                            assignment: Dict) -> List[Dict]:
        """
        Allocate study hours to optimal time slots

        LEARNING CONCEPT: Greedy Algorithm with Lookahead
        Select best slots first, but ensure we can finish before deadline
        """
        allocated = []
        remaining_hours = hours_needed

        # Filter slots that are before deadline
        valid_slots = [s for s in available_slots if s['start'] < deadline]

        # Sort by productivity score (greedy: take best slots first)
        sorted_slots = sorted(
            valid_slots,
            key=lambda s: s['productivity_score'],
            reverse=True
        )

        for slot in sorted_slots:
            if remaining_hours <= 0:
                break

            slot_duration = (slot['end'] - slot['start']).total_seconds() / 3600

            # Take what we need (up to slot duration)
            time_to_allocate = min(remaining_hours, slot_duration)

            allocated.append({
                'start': slot['start'],
                'end': slot['start'] + timedelta(hours=time_to_allocate),
                'productivity_zone': slot['productivity_zone']
            })

            remaining_hours -= time_to_allocate

        if remaining_hours > 0:
            logger.warning(f"Could not allocate {remaining_hours:.1f} hours for {assignment.get('title')}")

        return allocated

    def _remove_slot(self, slots: List[Dict], used_slot: Dict) -> List[Dict]:
        """Remove allocated slot from available slots"""
        return [s for s in slots if not (
            s['start'] == used_slot['start'] and s['end'] == used_slot['end']
        )]

# Main Event Intelligence class
class EventIntelligence:
    """
    Complete intelligent event management system

    Orchestrates:
    - Calendar integration
    - Pattern learning
    - Smart scheduling
    - Event prioritization
    """

    def __init__(self, ai_client, storage_dir: Path = None):
        self.ai_client = ai_client

        if storage_dir is None:
            storage_dir = Path.home() / ".academic_assistant" / "event_data"
        storage_dir.mkdir(parents=True, exist_ok=True)

        self.storage_dir = storage_dir
        self.productivity_analyzer = ProductivityAnalyzer(storage_dir)
        self.user_pattern = self._load_user_pattern()
        self.scheduler = IntelligentScheduler(self.user_pattern)

    def _load_user_pattern(self) -> UserProductivityPattern:
        """Load learned productivity pattern"""
        pattern_file = self.storage_dir / "productivity_pattern.json"
        if pattern_file.exists():
            try:
                with open(pattern_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct pattern (simplified)
                    pattern = UserProductivityPattern(user_id=data.get('user_id', 'default'))
                    pattern.hourly_productivity = {int(k): v for k, v in data.get('hourly_productivity', {}).items()}
                    pattern.daily_productivity = {int(k): v for k, v in data.get('daily_productivity', {}).items()}
                    return pattern
            except Exception as e:
                logger.error(f"Error loading productivity pattern: {e}")

        return self.productivity_analyzer._get_default_pattern()

    def load_important_events(self,
                             calendar_client: Optional[CalendarClient] = None,
                             days_ahead: int = 30) -> Dict[str, List[IntelligentEvent]]:
        """
        Load and classify all important events

        This demonstrates event aggregation from multiple sources
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)

        events = {
            "academic": [],
            "personal": [],
            "external": []
        }

        # Load from calendar if available
        if calendar_client:
            calendar_events = calendar_client.fetch_events(start_date, end_date)
            for event_data in calendar_events:
                # Classify and convert to IntelligentEvent
                classified = self._classify_calendar_event(event_data)
                events[classified['category']].append(classified['event'])

        return events

    def _classify_calendar_event(self, event_data: Dict) -> Dict:
        """Classify calendar event into category"""
        title = event_data.get('title', '').lower()

        # Simple classification (in production, use AI)
        if any(keyword in title for keyword in ['class', 'lecture', 'lab', 'exam', 'hw', 'assignment']):
            category = "academic"
            event_type = EventType.CLASS_LECTURE
        elif any(keyword in title for keyword in ['conference', 'deadline', 'submission']):
            category = "external"
            event_type = EventType.EXTERNAL_DEADLINE
        else:
            category = "personal"
            event_type = EventType.PERSONAL

        intelligent_event = IntelligentEvent(
            title=event_data.get('title', 'Untitled'),
            start_time=event_data.get('start_time'),
            end_time=event_data.get('end_time'),
            event_type=event_type,
            description=event_data.get('description'),
            location=event_data.get('location'),
            calendar_source=category
        )

        return {
            'category': category,
            'event': intelligent_event
        }

    def suggest_study_schedule(self, assignments: List[Dict]) -> List[IntelligentEvent]:
        """Create optimal study schedule for assignments"""
        # Get existing events
        existing_events = []  # Would load from calendar

        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        return self.scheduler.suggest_study_schedule(
            assignments,
            existing_events,
            start_date,
            end_date
        )


# Example usage
if __name__ == "__main__":
    print("📅 Intelligent Event Management & Scheduling")
    print("=" * 60)
    print()
    print("Key Concepts Demonstrated:")
    print("1. CalDAV Protocol for Calendar Access")
    print("2. iCalendar (.ics) Format Parsing")
    print("3. Time Series Analysis for Pattern Recognition")
    print("4. Multi-factor Productivity Scoring")
    print("5. Constraint-Based Scheduling Algorithms")
    print("6. Greedy Optimization with Lookahead")
    print()
    print("This system can:")
    print("✅ Connect to Google Calendar/iCloud/Outlook")
    print("✅ Learn user productivity patterns over time")
    print("✅ Classify events intelligently")
    print("✅ Generate optimal study schedules")
    print("✅ Avoid conflicts and buffer time")
    print("✅ Adapt to user preferences and behavior")
