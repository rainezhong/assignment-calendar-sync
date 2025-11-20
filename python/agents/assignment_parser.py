#!/usr/bin/env python3
"""
Intelligent Assignment Parser using Advanced NLP
Teaching concepts: Large Language Models, Information Extraction, Structured Data Generation
"""

import re
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Rich Type System for Data Validation
# Modern Python uses enums and dataclasses for type safety

class AssignmentType(Enum):
    """Enumeration of assignment types for better categorization"""
    HOMEWORK = "homework"
    PROJECT = "project"
    EXAM = "exam"
    QUIZ = "quiz"
    ESSAY = "essay"
    LAB = "lab"
    PRESENTATION = "presentation"
    DISCUSSION = "discussion"
    READING = "reading"
    OTHER = "other"

class UrgencyLevel(Enum):
    """Assignment urgency based on due date and importance"""
    OVERDUE = "overdue"
    CRITICAL = "critical"    # Due within 24 hours
    HIGH = "high"           # Due within 3 days
    MEDIUM = "medium"       # Due within 1 week
    LOW = "low"             # Due beyond 1 week

@dataclass
class ParsedAssignment:
    """
    Rich assignment data structure with validation and computed properties

    This demonstrates advanced Python features:
    - Dataclasses with default factories
    - Property methods for computed values
    - Type hints for better IDE support
    - Validation in __post_init__
    """
    title: str
    raw_text: str
    course: Optional[str] = None
    due_date: Optional[datetime] = None
    assignment_type: AssignmentType = AssignmentType.OTHER
    points_possible: Optional[float] = None
    description: Optional[str] = None
    requirements: List[str] = field(default_factory=list)
    submission_method: Optional[str] = None
    platform: str = "unknown"
    platform_id: Optional[str] = None
    extraction_confidence: float = 0.0
    parsing_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize data after initialization"""
        if not self.title:
            raise ValueError("Assignment title cannot be empty")

        if self.extraction_confidence < 0 or self.extraction_confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")

        # Clean up title
        self.title = self.title.strip()

        # Set parsing timestamp
        self.parsing_metadata['parsed_at'] = datetime.now().isoformat()

    @property
    def urgency_level(self) -> UrgencyLevel:
        """Computed property for assignment urgency"""
        if not self.due_date:
            return UrgencyLevel.LOW

        now = datetime.now()
        if self.due_date < now:
            return UrgencyLevel.OVERDUE

        time_until_due = self.due_date - now

        if time_until_due <= timedelta(days=1):
            return UrgencyLevel.CRITICAL
        elif time_until_due <= timedelta(days=3):
            return UrgencyLevel.HIGH
        elif time_until_due <= timedelta(days=7):
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW

    @property
    def days_until_due(self) -> Optional[float]:
        """Days until assignment is due (can be negative if overdue)"""
        if not self.due_date:
            return None

        delta = self.due_date - datetime.now()
        return delta.total_seconds() / (24 * 3600)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'title': self.title,
            'course': self.course,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assignment_type': self.assignment_type.value,
            'points_possible': self.points_possible,
            'description': self.description,
            'requirements': self.requirements,
            'submission_method': self.submission_method,
            'platform': self.platform,
            'platform_id': self.platform_id,
            'urgency_level': self.urgency_level.value,
            'days_until_due': self.days_until_due,
            'extraction_confidence': self.extraction_confidence,
            'parsing_metadata': self.parsing_metadata
        }

# LEARNING CONCEPT 2: Advanced Prompt Engineering with Chain-of-Thought
# This shows how to structure prompts for complex reasoning tasks

class IntelligentAssignmentParser:
    """
    Advanced assignment parser using Large Language Models

    Teaching concepts:
    - Prompt engineering with examples
    - Chain-of-thought reasoning
    - Structured output generation
    - Error handling and validation
    - Confidence scoring
    """

    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.parsing_examples = self._load_parsing_examples()
        self.date_patterns = self._compile_date_patterns()

    def _load_parsing_examples(self) -> List[Dict[str, str]]:
        """
        Few-shot learning examples for better parsing

        LEARNING CONCEPT: Few-shot prompting
        Providing examples teaches the AI the expected format and reasoning
        """
        return [
            {
                "input": "Problem Set 3 - CS 106A - Due Thursday, Oct 15 at 11:59 PM - Worth 100 points",
                "analysis": "This is clearly a homework assignment for CS 106A due on a specific date with point value",
                "output": {
                    "title": "Problem Set 3",
                    "course": "CS 106A",
                    "due_date": "2024-10-15T23:59:00",
                    "assignment_type": "homework",
                    "points_possible": 100.0,
                    "confidence": 0.95
                }
            },
            {
                "input": "Final Exam - ECON 101 - Monday December 12, 2-4 PM, Memorial Hall",
                "analysis": "This is an exam with specific time and location information",
                "output": {
                    "title": "Final Exam",
                    "course": "ECON 101",
                    "due_date": "2024-12-12T14:00:00",
                    "assignment_type": "exam",
                    "description": "Memorial Hall, 2-4 PM",
                    "confidence": 0.90
                }
            },
            {
                "input": "Essay on Climate Change - minimum 1000 words, cite 5 sources, submit via Canvas",
                "analysis": "This is an essay assignment with specific requirements and submission method",
                "output": {
                    "title": "Essay on Climate Change",
                    "assignment_type": "essay",
                    "requirements": ["minimum 1000 words", "cite 5 sources"],
                    "submission_method": "Canvas",
                    "confidence": 0.85
                }
            }
        ]

    def _compile_date_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for date extraction

        LEARNING CONCEPT: Hybrid AI + Traditional Programming
        Use regex for structured data, AI for understanding context
        """
        patterns = [
            # October 15, 2024 at 11:59 PM
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})\s+at\s+(\d{1,2}):(\d{2})\s*(AM|PM)',
            # Oct 15 at 11:59 PM
            r'(\w{3})\s+(\d{1,2})\s+at\s+(\d{1,2}):(\d{2})\s*(AM|PM)',
            # Thursday, October 15
            r'(\w+),?\s+(\w+)\s+(\d{1,2})',
            # 10/15/2024 11:59 PM
            r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)',
            # Due: Friday
            r'due:?\s*(\w+)',
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    # LEARNING CONCEPT 3: Structured Output Generation with LLMs
    # Modern AI systems can generate structured data reliably

    async def parse_assignment_text(self, text: str, context: Dict[str, Any] = None) -> ParsedAssignment:
        """
        Parse assignment text using advanced NLP and structured reasoning

        This method demonstrates:
        - Structured prompt engineering
        - Chain-of-thought reasoning
        - Error handling and validation
        - Confidence scoring
        """
        if not text or not text.strip():
            raise ValueError("Cannot parse empty text")

        # Prepare context information
        context = context or {}
        current_date = datetime.now().strftime("%Y-%m-%d")
        platform = context.get('platform', 'unknown')

        # ADVANCED PROMPT: Notice the structure and reasoning chain
        parsing_prompt = f"""
        You are an expert academic assistant that extracts assignment information from university text.

        CURRENT DATE: {current_date}
        PLATFORM: {platform}

        TEXT TO PARSE:
        "{text}"

        INSTRUCTIONS:
        1. First, analyze what type of content this is
        2. Extract key information using chain-of-thought reasoning
        3. Determine confidence based on clarity of information
        4. Output structured JSON

        REASONING PROCESS:
        - Is this clearly an assignment, or could it be something else?
        - What type of assignment is this? (homework, exam, project, etc.)
        - When is it due? (look for dates, times, relative references)
        - What course is it for?
        - Are there specific requirements mentioned?
        - How confident am I in each piece of extracted information?

        EXAMPLES OF GOOD PARSING:
        {json.dumps(self.parsing_examples, indent=2)}

        OUTPUT FORMAT:
        {{
            "reasoning": "Step-by-step analysis of the text",
            "is_assignment": true/false,
            "extracted_data": {{
                "title": "Assignment title (required)",
                "course": "Course name/code or null",
                "due_date": "ISO format date or null",
                "assignment_type": "homework|project|exam|quiz|essay|lab|presentation|discussion|reading|other",
                "points_possible": "Point value as number or null",
                "description": "Brief description or null",
                "requirements": ["list", "of", "requirements"],
                "submission_method": "How to submit or null",
                "platform_hints": {{
                    "likely_url": "URL if mentioned",
                    "platform_specific_id": "ID if found"
                }}
            }},
            "confidence_scores": {{
                "overall": 0.0-1.0,
                "title": 0.0-1.0,
                "due_date": 0.0-1.0,
                "assignment_type": 0.0-1.0
            }},
            "potential_issues": ["list", "of", "any", "ambiguities"]
        }}

        IMPORTANT:
        - Only mark is_assignment=true if you're confident this is actually an assignment
        - Use null for missing information rather than guessing
        - Be conservative with confidence scores
        - Include reasoning for your decisions
        """

        try:
            # Get structured response from AI
            response = await self.ai_client.structured_completion(
                prompt=parsing_prompt,
                response_format="json"
            )

            parsed_response = json.loads(response)

            # Validate AI response structure
            if not self._validate_ai_response(parsed_response):
                raise ValueError("Invalid AI response structure")

            # Convert to ParsedAssignment object
            assignment = self._convert_to_assignment(parsed_response, text, platform)

            # Post-process and enhance
            assignment = await self._enhance_assignment(assignment, context)

            logger.info(f"Successfully parsed assignment: {assignment.title} (confidence: {assignment.extraction_confidence:.2f})")
            return assignment

        except Exception as e:
            logger.error(f"Parsing failed for text '{text[:100]}...': {e}")

            # Fallback to basic parsing
            return self._fallback_parse(text, platform)

    def _validate_ai_response(self, response: Dict[str, Any]) -> bool:
        """Validate the structure of AI response"""
        required_fields = ['reasoning', 'is_assignment', 'extracted_data', 'confidence_scores']

        if not all(field in response for field in required_fields):
            return False

        if not isinstance(response['is_assignment'], bool):
            return False

        if not isinstance(response['confidence_scores'], dict):
            return False

        return True

    def _convert_to_assignment(self, ai_response: Dict[str, Any], raw_text: str, platform: str) -> ParsedAssignment:
        """Convert AI response to ParsedAssignment object"""
        if not ai_response['is_assignment']:
            raise ValueError("Text does not appear to be an assignment")

        extracted = ai_response['extracted_data']
        confidence = ai_response['confidence_scores']['overall']

        # Parse due date if provided
        due_date = None
        if extracted.get('due_date'):
            try:
                due_date = datetime.fromisoformat(extracted['due_date'].replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Could not parse due date: {extracted['due_date']}")

        # Determine assignment type
        assignment_type = AssignmentType.OTHER
        type_str = extracted.get('assignment_type', 'other').lower()
        try:
            assignment_type = AssignmentType(type_str)
        except ValueError:
            logger.warning(f"Unknown assignment type: {type_str}")

        return ParsedAssignment(
            title=extracted['title'],
            raw_text=raw_text,
            course=extracted.get('course'),
            due_date=due_date,
            assignment_type=assignment_type,
            points_possible=extracted.get('points_possible'),
            description=extracted.get('description'),
            requirements=extracted.get('requirements', []),
            submission_method=extracted.get('submission_method'),
            platform=platform,
            platform_id=extracted.get('platform_hints', {}).get('platform_specific_id'),
            extraction_confidence=confidence,
            parsing_metadata={
                'ai_reasoning': ai_response['reasoning'],
                'confidence_breakdown': ai_response['confidence_scores'],
                'potential_issues': ai_response.get('potential_issues', []),
                'parsing_method': 'ai_structured'
            }
        )

    async def _enhance_assignment(self, assignment: ParsedAssignment, context: Dict[str, Any]) -> ParsedAssignment:
        """
        Post-process assignment to add additional intelligence

        LEARNING CONCEPT: Progressive Enhancement
        Start with basic extraction, then add intelligence layers
        """

        # Enhance due date with smart defaults
        if not assignment.due_date and context.get('default_due_time'):
            assignment.due_date = self._infer_due_date(assignment.raw_text, context)

        # Enhance course information
        if not assignment.course and context.get('current_courses'):
            assignment.course = self._infer_course(assignment.raw_text, context['current_courses'])

        # Add intelligent categorization
        assignment.assignment_type = self._refine_assignment_type(assignment)

        return assignment

    def _infer_due_date(self, text: str, context: Dict[str, Any]) -> Optional[datetime]:
        """Attempt to infer due date using regex and context"""
        for pattern in self.date_patterns:
            match = pattern.search(text)
            if match:
                try:
                    # This would contain logic to parse different date formats
                    # For brevity, returning None here
                    return None
                except ValueError:
                    continue
        return None

    def _infer_course(self, text: str, available_courses: List[str]) -> Optional[str]:
        """Match assignment text to known courses"""
        text_lower = text.lower()

        for course in available_courses:
            course_variations = [
                course.lower(),
                course.replace(' ', '').lower(),
                course.split()[0].lower() if ' ' in course else course.lower()
            ]

            if any(variation in text_lower for variation in course_variations):
                return course

        return None

    def _refine_assignment_type(self, assignment: ParsedAssignment) -> AssignmentType:
        """Use additional heuristics to refine assignment type"""
        title = assignment.title.lower()
        description = (assignment.description or '').lower()
        combined_text = f"{title} {description}"

        # Keyword-based classification
        type_keywords = {
            AssignmentType.HOMEWORK: ['homework', 'problem set', 'pset', 'hw', 'assignment'],
            AssignmentType.PROJECT: ['project', 'final project', 'group project'],
            AssignmentType.EXAM: ['exam', 'test', 'midterm', 'final', 'quiz'],
            AssignmentType.ESSAY: ['essay', 'paper', 'report', 'write', 'composition'],
            AssignmentType.LAB: ['lab', 'laboratory', 'experiment'],
            AssignmentType.PRESENTATION: ['presentation', 'present', 'demo'],
        }

        for assignment_type, keywords in type_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return assignment_type

        return assignment.assignment_type  # Keep original if no match

    def _fallback_parse(self, text: str, platform: str) -> ParsedAssignment:
        """Basic fallback parsing when AI fails"""
        logger.warning("Using fallback parsing method")

        return ParsedAssignment(
            title=text[:100] if len(text) > 100 else text,
            raw_text=text,
            platform=platform,
            extraction_confidence=0.1,  # Very low confidence
            parsing_metadata={
                'parsing_method': 'fallback',
                'note': 'AI parsing failed, using basic extraction'
            }
        )

    # LEARNING CONCEPT 4: Batch Processing with Async/Await
    # Real systems need to handle multiple items efficiently

    async def parse_multiple_assignments(self, texts: List[str], context: Dict[str, Any] = None) -> List[ParsedAssignment]:
        """
        Parse multiple assignments concurrently

        This demonstrates:
        - Async/await for concurrent processing
        - Error handling in batch operations
        - Progress tracking
        - Rate limiting for API calls
        """
        if not texts:
            return []

        context = context or {}
        assignments = []

        # Process in batches to avoid overwhelming the AI API
        batch_size = context.get('batch_size', 5)

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Create concurrent tasks for this batch
            tasks = [
                self.parse_assignment_text(text, context)
                for text in batch
            ]

            # Execute batch concurrently
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, ParsedAssignment):
                        assignments.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Batch parsing error: {result}")

                # Rate limiting between batches
                if i + batch_size < len(texts):
                    await asyncio.sleep(1)  # 1 second delay between batches

            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                continue

        logger.info(f"Parsed {len(assignments)} assignments from {len(texts)} texts")
        return assignments

# LEARNING CONCEPT 5: Performance Monitoring and Analytics
class ParsingAnalytics:
    """Track parsing performance and accuracy"""

    def __init__(self):
        self.parse_times = []
        self.confidence_scores = []
        self.error_count = 0
        self.success_count = 0

    def record_parse(self, duration: float, confidence: float, success: bool):
        """Record parsing metrics"""
        if success:
            self.parse_times.append(duration)
            self.confidence_scores.append(confidence)
            self.success_count += 1
        else:
            self.error_count += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        if not self.parse_times:
            return {"status": "no_data"}

        return {
            "success_rate": self.success_count / (self.success_count + self.error_count),
            "average_parse_time": sum(self.parse_times) / len(self.parse_times),
            "average_confidence": sum(self.confidence_scores) / len(self.confidence_scores),
            "total_parsed": len(self.parse_times),
            "total_errors": self.error_count
        }

# Example usage and testing
if __name__ == "__main__":
    print("🧠 Intelligent Assignment Parser")
    print("=" * 50)
    print()
    print("Advanced concepts demonstrated:")
    print("1. Rich type system with enums and dataclasses")
    print("2. Advanced prompt engineering with chain-of-thought")
    print("3. Structured output generation with LLMs")
    print("4. Batch processing with async/await")
    print("5. Performance monitoring and analytics")
    print()
    print("This parser can understand:")
    print("✅ Natural language assignment descriptions")
    print("✅ Complex due date formats")
    print("✅ Assignment types and requirements")
    print("✅ Confidence scoring for reliability")
    print("✅ Batch processing for efficiency")