#!/usr/bin/env python3
"""
Smart Adaptive Reminder System
Teaching concepts: Machine Learning for Estimation, Push Notifications, Adaptive Algorithms, Feature Engineering
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging
from enum import Enum
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Feature Engineering for ML
# Transform raw data into features that predict difficulty

class DifficultyLevel(Enum):
    """Assignment difficulty classification"""
    TRIVIAL = "trivial"       # < 1 hour
    EASY = "easy"             # 1-3 hours
    MODERATE = "moderate"     # 3-8 hours
    HARD = "hard"             # 8-15 hours
    VERY_HARD = "very_hard"   # > 15 hours

@dataclass
class DifficultyEstimate:
    """
    ML-based difficulty estimation

    Teaching Concepts:
    - Feature engineering
    - Multi-factor estimation
    - Confidence intervals
    - Explain ability in ML
    """
    difficulty_level: DifficultyLevel
    estimated_hours: float
    confidence: float  # 0-1
    prep_time_before_due: timedelta  # When to start
    work_time_before_due: timedelta  # When to do main work

    # Feature breakdown (for explainability)
    features_used: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""

    # Adaptive timing
    milestones: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_features(cls, features: Dict[str, float]) -> 'DifficultyEstimate':
        """
        Create difficulty estimate from features

        LEARNING CONCEPT: Feature-based Prediction
        Combine multiple signals to predict difficulty
        """
        # Calculate base difficulty score (0-1)
        score = 0.0

        # Weight different features
        weights = {
            'assignment_type_score': 0.3,
            'course_difficulty': 0.25,
            'length_complexity': 0.2,
            'prerequisites_score': 0.15,
            'time_available': 0.1
        }

        for feature, weight in weights.items():
            score += features.get(feature, 0.5) * weight

        # Map score to difficulty level
        if score < 0.2:
            level = DifficultyLevel.TRIVIAL
            hours = 0.5
        elif score < 0.4:
            level = DifficultyLevel.EASY
            hours = 2.0
        elif score < 0.6:
            level = DifficultyLevel.MODERATE
            hours = 5.0
        elif score < 0.8:
            level = DifficultyLevel.HARD
            hours = 10.0
        else:
            level = DifficultyLevel.VERY_HARD
            hours = 20.0

        # Calculate timing recommendations
        prep_time = timedelta(days=max(2, int(hours / 3)))
        work_time = timedelta(days=max(1, int(hours / 5)))

        # Generate milestones
        milestones = []
        if hours > 3:
            milestones.append({
                'name': 'Research & Planning',
                'time_before_due': prep_time,
                'duration_hours': hours * 0.2,
                'description': 'Understand requirements and gather resources'
            })

        if hours > 1:
            milestones.append({
                'name': 'First Draft / Initial Work',
                'time_before_due': work_time,
                'duration_hours': hours * 0.5,
                'description': 'Complete majority of the work'
            })

        milestones.append({
            'name': 'Review & Polish',
            'time_before_due': timedelta(days=1),
            'duration_hours': hours * 0.2,
            'description': 'Review, test, and finalize'
        })

        milestones.append({
            'name': 'Final Submission',
            'time_before_due': timedelta(hours=1),
            'duration_hours': 0.25,
            'description': 'Upload and verify submission'
        })

        return cls(
            difficulty_level=level,
            estimated_hours=hours,
            confidence=0.7,  # Would be calculated from feature variance
            prep_time_before_due=prep_time,
            work_time_before_due=work_time,
            features_used=features,
            reasoning=f"Based on {len(features)} features, estimated as {level.value}",
            milestones=milestones
        )

# LEARNING CONCEPT 2: Feature Extraction Pipeline
# Extract predictive features from assignment data

class DifficultyPredictor:
    """
    ML-based difficulty predictor

    Teaching Concepts:
    - Feature extraction pipeline
    - Text analysis for complexity
    - Historical data learning
    - Transfer learning from similar assignments
    """

    def __init__(self, ai_client, storage_dir: Path):
        self.ai_client = ai_client
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Historical difficulty data
        self.difficulty_db = self._init_difficulty_db()

    def _init_difficulty_db(self) -> sqlite3.Connection:
        """Initialize database for storing difficulty history"""
        db_path = self.storage_dir / "difficulty_history.db"
        conn = sqlite3.connect(str(db_path))

        conn.execute("""
            CREATE TABLE IF NOT EXISTS difficulty_history (
                id INTEGER PRIMARY KEY,
                assignment_hash TEXT UNIQUE,
                assignment_title TEXT,
                course TEXT,
                assignment_type TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                estimated_difficulty TEXT,
                actual_difficulty TEXT,
                features_json TEXT,
                created_at DATETIME,
                completed_at DATETIME
            )
        """)

        conn.commit()
        return conn

    async def estimate_difficulty(self, assignment: Dict[str, Any]) -> DifficultyEstimate:
        """
        Estimate assignment difficulty using ML

        This demonstrates:
        - Multi-source feature extraction
        - AI-enhanced text analysis
        - Historical pattern matching
        - Ensemble prediction
        """
        # Extract features from assignment
        features = await self._extract_features(assignment)

        # Check historical data for similar assignments
        historical_estimate = self._get_historical_estimate(assignment, features)

        if historical_estimate:
            # Adjust features based on history
            features = self._adjust_features_with_history(features, historical_estimate)

        # Create difficulty estimate
        estimate = DifficultyEstimate.from_features(features)

        # Store estimate for future learning
        self._store_estimate(assignment, estimate, features)

        logger.info(f"Estimated difficulty: {estimate.difficulty_level.value} ({estimate.estimated_hours:.1f} hours)")
        return estimate

    async def _extract_features(self, assignment: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract predictive features from assignment

        LEARNING CONCEPT: Feature Engineering
        Transform raw data into numerical features for ML
        """
        features = {}

        # Feature 1: Assignment type complexity
        type_complexity = {
            'quiz': 0.1,
            'homework': 0.3,
            'lab': 0.4,
            'essay': 0.6,
            'project': 0.8,
            'exam': 0.7,
            'other': 0.5
        }
        assignment_type = assignment.get('type', 'other').lower()
        features['assignment_type_score'] = type_complexity.get(assignment_type, 0.5)

        # Feature 2: Course difficulty (would be learned over time)
        course = assignment.get('course', '')
        features['course_difficulty'] = self._get_course_difficulty(course)

        # Feature 3: Length/complexity from description
        description = assignment.get('description', '')
        title = assignment.get('title', '')
        features['length_complexity'] = await self._analyze_text_complexity(description, title)

        # Feature 4: Points possible (normalized)
        points = assignment.get('points_possible', 100)
        features['points_score'] = min(1.0, points / 200.0)  # Normalize to 0-1

        # Feature 5: Requirements complexity
        requirements = assignment.get('requirements', [])
        features['requirements_count'] = min(1.0, len(requirements) / 10.0)

        # Feature 6: Time available until deadline
        due_date = assignment.get('due_date')
        if due_date:
            days_until_due = (due_date - datetime.now()).days
            # Less time = higher complexity/urgency
            features['time_available'] = max(0.0, min(1.0, days_until_due / 14.0))
        else:
            features['time_available'] = 0.5

        # Feature 7: Prerequisites/dependencies mentioned
        features['prerequisites_score'] = await self._analyze_prerequisites(description, title)

        logger.debug(f"Extracted {len(features)} features: {features}")
        return features

    def _get_course_difficulty(self, course: str) -> float:
        """
        Get learned difficulty for a course

        LEARNING CONCEPT: Transfer Learning
        Use historical data from same course to predict difficulty
        """
        if not course:
            return 0.5

        # Query historical difficulty for this course
        cursor = self.difficulty_db.execute("""
            SELECT AVG(actual_hours) as avg_hours
            FROM difficulty_history
            WHERE course = ?
            AND actual_hours IS NOT NULL
        """, (course,))

        result = cursor.fetchone()
        if result and result[0]:
            avg_hours = result[0]
            # Normalize to 0-1 (assuming max 20 hours)
            return min(1.0, avg_hours / 20.0)

        return 0.5  # Default if no history

    async def _analyze_text_complexity(self, description: str, title: str) -> float:
        """
        Analyze text to estimate complexity

        LEARNING CONCEPT: NLP for Feature Extraction
        Use AI to understand assignment complexity from description
        """
        if not description and not title:
            return 0.5

        combined_text = f"{title}\n{description}"

        # Use AI to analyze complexity
        complexity_prompt = f"""
Analyze this assignment description and rate its complexity on a scale of 0-1.

ASSIGNMENT:
{combined_text[:500]}

Consider:
- Technical depth required
- Number of steps/components
- Skill level needed
- Ambiguity vs clarity of requirements

Return ONLY a number between 0 and 1 where:
- 0 = Very simple, clear, quick task
- 0.5 = Moderate complexity
- 1 = Very complex, multi-part, advanced skills needed

Output format: {{"complexity": 0.0-1.0, "reasoning": "brief explanation"}}
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=complexity_prompt,
                response_format="json"
            )

            analysis = json.loads(response)
            complexity = analysis.get('complexity', 0.5)
            logger.debug(f"Text complexity: {complexity} - {analysis.get('reasoning', '')}")
            return complexity

        except Exception as e:
            logger.error(f"Text complexity analysis failed: {e}")
            # Fallback: simple heuristics
            word_count = len(combined_text.split())
            return min(1.0, word_count / 500)  # Longer = more complex

    async def _analyze_prerequisites(self, description: str, title: str) -> float:
        """Detect prerequisite complexity from text"""
        combined = f"{title} {description}".lower()

        # Keywords indicating complexity
        complex_keywords = [
            'advanced', 'prerequisite', 'requires', 'must know',
            'building on', 'continuation', 'extends', 'assumes'
        ]

        matches = sum(1 for keyword in complex_keywords if keyword in combined)
        return min(1.0, matches / 5)

    def _get_historical_estimate(self,
                                 assignment: Dict[str, Any],
                                 features: Dict[str, float]) -> Optional[Dict]:
        """Find similar past assignments"""
        # Simple similarity: same course + type
        course = assignment.get('course', '')
        assignment_type = assignment.get('type', '')

        if not course:
            return None

        cursor = self.difficulty_db.execute("""
            SELECT assignment_title, actual_hours, features_json
            FROM difficulty_history
            WHERE course = ?
            AND assignment_type = ?
            AND actual_hours IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 5
        """, (course, assignment_type))

        results = cursor.fetchall()
        if not results:
            return None

        # Average similar assignments
        avg_hours = sum(r[1] for r in results) / len(results)

        return {
            'avg_hours': avg_hours,
            'sample_size': len(results),
            'confidence': min(1.0, len(results) / 5)  # More samples = higher confidence
        }

    def _adjust_features_with_history(self,
                                     features: Dict[str, float],
                                     historical: Dict) -> Dict[str, float]:
        """Adjust features based on historical data"""
        adjusted = features.copy()

        # Blend predicted difficulty with historical average
        historical_score = min(1.0, historical['avg_hours'] / 20.0)
        confidence = historical['confidence']

        # Weighted average (more history = more weight)
        for key in features:
            if 'difficulty' in key or 'complexity' in key:
                adjusted[key] = (
                    features[key] * (1 - confidence) +
                    historical_score * confidence
                )

        return adjusted

    def _store_estimate(self,
                       assignment: Dict[str, Any],
                       estimate: DifficultyEstimate,
                       features: Dict[str, float]):
        """Store estimate for future learning"""
        assignment_hash = hashlib.md5(
            f"{assignment.get('title', '')}{assignment.get('course', '')}".encode()
        ).hexdigest()

        try:
            self.difficulty_db.execute("""
                INSERT OR REPLACE INTO difficulty_history
                (assignment_hash, assignment_title, course, assignment_type,
                 estimated_hours, estimated_difficulty, features_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment_hash,
                assignment.get('title', ''),
                assignment.get('course', ''),
                assignment.get('type', 'other'),
                estimate.estimated_hours,
                estimate.difficulty_level.value,
                json.dumps(features),
                datetime.now()
            ))
            self.difficulty_db.commit()
        except Exception as e:
            logger.error(f"Failed to store difficulty estimate: {e}")

    def record_actual_difficulty(self,
                                assignment_hash: str,
                                actual_hours: float,
                                actual_difficulty: DifficultyLevel):
        """
        Record actual difficulty after completion

        LEARNING CONCEPT: Active Learning Loop
        Learn from actual outcomes to improve future predictions
        """
        try:
            self.difficulty_db.execute("""
                UPDATE difficulty_history
                SET actual_hours = ?,
                    actual_difficulty = ?,
                    completed_at = ?
                WHERE assignment_hash = ?
            """, (actual_hours, actual_difficulty.value, datetime.now(), assignment_hash))
            self.difficulty_db.commit()

            logger.info(f"Recorded actual difficulty: {actual_hours:.1f} hours ({actual_difficulty.value})")
        except Exception as e:
            logger.error(f"Failed to record actual difficulty: {e}")

# LEARNING CONCEPT 3: Adaptive Reminder Scheduling
# Reminders that adapt to user behavior and assignment difficulty

@dataclass
class SmartReminder:
    """
    Intelligent reminder with adaptive timing

    Teaching Concepts:
    - Personalization algorithms
    - Temporal scheduling
    - User behavior adaptation
    """
    reminder_id: str
    assignment_id: str
    assignment_title: str
    reminder_type: str  # prep, start, progress, final, submit
    scheduled_time: datetime
    message: str
    importance: float  # 0-1
    is_sent: bool = False
    sent_at: Optional[datetime] = None

    # Adaptive features
    user_response_rate: float = 0.5  # Historical engagement with this type
    optimal_lead_time: timedelta = timedelta(hours=24)

    @property
    def is_overdue(self) -> bool:
        """Check if reminder time has passed"""
        return datetime.now() > self.scheduled_time and not self.is_sent

    def to_notification(self) -> Dict[str, Any]:
        """Convert to notification format"""
        return {
            'title': f"📚 {self.reminder_type.title()}: {self.assignment_title}",
            'body': self.message,
            'scheduled_time': self.scheduled_time.isoformat(),
            'importance': self.importance,
            'action_url': f"assignment://{self.assignment_id}"
        }

class UserBehaviorAnalyzer:
    """
    Analyze user behavior to personalize reminders

    Teaching Concepts:
    - Behavioral analytics
    - Pattern extraction from event logs
    - Preference learning
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.behavior_db = self._init_behavior_db()

    def _init_behavior_db(self) -> sqlite3.Connection:
        """Initialize behavior tracking database"""
        db_path = self.storage_dir / "user_behavior.db"
        conn = sqlite3.connect(str(db_path))

        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminder_interactions (
                id INTEGER PRIMARY KEY,
                reminder_id TEXT,
                reminder_type TEXT,
                sent_at DATETIME,
                opened_at DATETIME,
                action_taken TEXT,  # dismissed, snoozed, completed
                time_to_action_seconds INTEGER,
                assignment_completed BOOLEAN,
                created_at DATETIME
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS completion_patterns (
                id INTEGER PRIMARY KEY,
                assignment_type TEXT,
                started_at DATETIME,
                completed_at DATETIME,
                estimated_hours REAL,
                actual_hours REAL,
                started_on_time BOOLEAN,
                completed_on_time BOOLEAN,
                created_at DATETIME
            )
        """)

        conn.commit()
        return conn

    def get_completion_patterns(self, assignment_type: str = None) -> Dict[str, Any]:
        """
        Analyze historical completion patterns

        LEARNING CONCEPT: Time Series Pattern Analysis
        Extract behavioral patterns from historical data
        """
        query = """
            SELECT
                assignment_type,
                AVG(actual_hours) as avg_hours,
                AVG(CAST(completed_on_time AS REAL)) as on_time_rate,
                AVG(CAST(started_on_time AS REAL)) as start_on_time_rate,
                COUNT(*) as sample_size
            FROM completion_patterns
        """

        params = []
        if assignment_type:
            query += " WHERE assignment_type = ?"
            params.append(assignment_type)

        query += " GROUP BY assignment_type"

        cursor = self.behavior_db.execute(query, params)
        results = cursor.fetchall()

        patterns = {}
        for row in results:
            patterns[row[0]] = {
                'avg_hours': row[1],
                'on_time_rate': row[2],
                'start_on_time_rate': row[3],
                'sample_size': row[4]
            }

        return patterns

    def get_optimal_reminder_timing(self, reminder_type: str) -> timedelta:
        """
        Calculate optimal reminder timing based on user response

        LEARNING CONCEPT: Response Time Optimization
        Learn when user is most responsive to reminders
        """
        cursor = self.behavior_db.execute("""
            SELECT AVG(time_to_action_seconds)
            FROM reminder_interactions
            WHERE reminder_type = ?
            AND action_taken IN ('completed', 'started')
            AND time_to_action_seconds < 86400  -- Within 24 hours
        """, (reminder_type,))

        result = cursor.fetchone()
        if result and result[0]:
            # User typically acts after this many seconds
            avg_response_seconds = result[0]
            # Send reminder that much earlier
            return timedelta(seconds=avg_response_seconds)

        # Defaults by reminder type
        defaults = {
            'prep': timedelta(days=3),
            'start': timedelta(days=2),
            'progress': timedelta(days=1),
            'final': timedelta(hours=6),
            'submit': timedelta(hours=1)
        }

        return defaults.get(reminder_type, timedelta(days=1))

    def record_reminder_interaction(self,
                                   reminder_id: str,
                                   reminder_type: str,
                                   action: str):
        """Record user interaction with reminder"""
        try:
            self.behavior_db.execute("""
                INSERT INTO reminder_interactions
                (reminder_id, reminder_type, sent_at, action_taken, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (reminder_id, reminder_type, datetime.now(), action, datetime.now()))
            self.behavior_db.commit()
        except Exception as e:
            logger.error(f"Failed to record reminder interaction: {e}")

# Main Smart Reminders class
class SmartReminders:
    """
    Complete adaptive reminder system

    Orchestrates:
    - Difficulty estimation
    - Behavioral learning
    - Adaptive scheduling
    - Personalized messaging
    """

    def __init__(self, ai_client, storage_dir: Path = None):
        self.ai_client = ai_client

        if storage_dir is None:
            storage_dir = Path.home() / ".academic_assistant" / "reminders"
        storage_dir.mkdir(parents=True, exist_ok=True)

        self.storage_dir = storage_dir
        self.difficulty_predictor = DifficultyPredictor(ai_client, storage_dir)
        self.behavior_analyzer = UserBehaviorAnalyzer(storage_dir)

        # Reminder storage
        self.reminders_db = self._init_reminders_db()

    def _init_reminders_db(self) -> sqlite3.Connection:
        """Initialize reminders database"""
        db_path = self.storage_dir / "reminders.db"
        conn = sqlite3.connect(str(db_path))

        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_id TEXT PRIMARY KEY,
                assignment_id TEXT,
                assignment_title TEXT,
                reminder_type TEXT,
                scheduled_time DATETIME,
                message TEXT,
                importance REAL,
                is_sent BOOLEAN DEFAULT 0,
                sent_at DATETIME,
                created_at DATETIME
            )
        """)

        conn.commit()
        return conn

    async def create_adaptive_reminders(self, assignment: Dict[str, Any]) -> List[SmartReminder]:
        """
        Create personalized reminder schedule

        This demonstrates:
        - ML-based difficulty estimation
        - Behavioral pattern integration
        - Adaptive timing
        - Personalized messaging
        """
        # Step 1: Estimate difficulty
        difficulty = await self.difficulty_predictor.estimate_difficulty(assignment)

        # Step 2: Get user completion patterns
        user_history = self.behavior_analyzer.get_completion_patterns(
            assignment.get('type', 'other')
        )

        # Step 3: Create reminders for each milestone
        reminders = []
        due_date = assignment.get('due_date')

        if not due_date:
            logger.warning("No due date - skipping reminders")
            return []

        # Create reminder for each milestone
        for milestone in difficulty.milestones:
            # Calculate reminder time with adaptive adjustment
            base_reminder_time = due_date - milestone['time_before_due']

            # Adjust based on user behavior
            optimal_lead = self.behavior_analyzer.get_optimal_reminder_timing(
                milestone['name'].lower().split()[0]  # First word as type
            )

            # Apply adjustment if user has history
            if user_history:
                on_time_rate = user_history.get(assignment.get('type', 'other'), {}).get('start_on_time_rate', 0.5)

                # If user often starts late, remind earlier
                if on_time_rate < 0.5:
                    base_reminder_time -= timedelta(hours=12)

            # Create reminder
            reminder_id = hashlib.md5(
                f"{assignment.get('title', '')}{milestone['name']}{base_reminder_time}".encode()
            ).hexdigest()

            message = self._generate_reminder_message(
                assignment,
                milestone,
                difficulty
            )

            reminder = SmartReminder(
                reminder_id=reminder_id,
                assignment_id=assignment.get('id', ''),
                assignment_title=assignment.get('title', 'Assignment'),
                reminder_type=milestone['name'].lower().replace(' ', '_'),
                scheduled_time=base_reminder_time,
                message=message,
                importance=difficulty.estimated_hours / 20.0,  # Normalize to 0-1
                optimal_lead_time=optimal_lead
            )

            reminders.append(reminder)

            # Store in database
            self._store_reminder(reminder)

        logger.info(f"Created {len(reminders)} adaptive reminders for {assignment.get('title')}")
        return reminders

    def _generate_reminder_message(self,
                                   assignment: Dict[str, Any],
                                   milestone: Dict[str, Any],
                                   difficulty: DifficultyEstimate) -> str:
        """Generate contextual reminder message"""
        messages = {
            'Research & Planning': f"Time to start planning '{assignment.get('title')}'. "
                                 f"Estimated time: {milestone['duration_hours']:.1f} hours. "
                                 f"{milestone['description']}",

            'First Draft / Initial Work': f"Start working on '{assignment.get('title')}'. "
                                         f"Block out {milestone['duration_hours']:.1f} hours. "
                                         f"{milestone['description']}",

            'Review & Polish': f"Review your work on '{assignment.get('title')}'. "
                             f"Set aside {milestone['duration_hours']:.1f} hours for final touches.",

            'Final Submission': f"⏰ Submit '{assignment.get('title')}' soon! "
                              f"Due in 1 hour. Double-check requirements."
        }

        return messages.get(milestone['name'], milestone['description'])

    def _store_reminder(self, reminder: SmartReminder):
        """Store reminder in database"""
        try:
            self.reminders_db.execute("""
                INSERT OR REPLACE INTO reminders
                (reminder_id, assignment_id, assignment_title, reminder_type,
                 scheduled_time, message, importance, is_sent, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                reminder.reminder_id,
                reminder.assignment_id,
                reminder.assignment_title,
                reminder.reminder_type,
                reminder.scheduled_time,
                reminder.message,
                reminder.importance,
                datetime.now()
            ))
            self.reminders_db.commit()
        except Exception as e:
            logger.error(f"Failed to store reminder: {e}")

    def get_pending_reminders(self) -> List[SmartReminder]:
        """Get all pending reminders that should be sent"""
        cursor = self.reminders_db.execute("""
            SELECT reminder_id, assignment_id, assignment_title, reminder_type,
                   scheduled_time, message, importance
            FROM reminders
            WHERE is_sent = 0
            AND scheduled_time <= ?
            ORDER BY importance DESC, scheduled_time ASC
        """, (datetime.now(),))

        reminders = []
        for row in cursor.fetchall():
            reminder = SmartReminder(
                reminder_id=row[0],
                assignment_id=row[1],
                assignment_title=row[2],
                reminder_type=row[3],
                scheduled_time=datetime.fromisoformat(row[4]),
                message=row[5],
                importance=row[6],
                is_sent=False
            )
            reminders.append(reminder)

        return reminders

    def mark_reminder_sent(self, reminder_id: str):
        """Mark reminder as sent"""
        try:
            self.reminders_db.execute("""
                UPDATE reminders
                SET is_sent = 1, sent_at = ?
                WHERE reminder_id = ?
            """, (datetime.now(), reminder_id))
            self.reminders_db.commit()
        except Exception as e:
            logger.error(f"Failed to mark reminder sent: {e}")

# Example usage
if __name__ == "__main__":
    print("🔔 Smart Adaptive Reminder System")
    print("=" * 60)
    print()
    print("Key Concepts Demonstrated:")
    print("1. Feature Engineering for ML Predictions")
    print("2. Transfer Learning from Historical Data")
    print("3. Behavioral Pattern Analysis")
    print("4. Adaptive Scheduling Algorithms")
    print("5. Active Learning Loop (improve from feedback)")
    print("6. Multi-factor Difficulty Estimation")
    print()
    print("This system can:")
    print("✅ Estimate assignment difficulty using ML")
    print("✅ Learn from past assignments to improve accuracy")
    print("✅ Analyze user completion patterns")
    print("✅ Create adaptive reminder schedules")
    print("✅ Personalize reminder timing based on behavior")
    print("✅ Generate contextual reminder messages")
    print("✅ Track reminder effectiveness and adapt")
