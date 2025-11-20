#!/usr/bin/env python3
"""
Universal LMS Agent - Base Architecture
Teaching concepts: Agent Design Patterns, Abstract Base Classes, Dependency Injection
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Protocol-Oriented Programming
# Protocols define behavior contracts without implementation
# This is more flexible than inheritance and follows composition over inheritance
class AIClient(Protocol):
    """Protocol for AI clients (OpenAI, Anthropic, etc.)"""
    async def analyze_image(self, image: bytes, prompt: str) -> str: ...
    async def structured_completion(self, prompt: str, response_format: str = "json") -> Dict[str, Any]: ...
    async def simple_completion(self, prompt: str) -> str: ...

class BrowserDriver(Protocol):
    """Protocol for browser automation (Playwright, Selenium, etc.)"""
    async def navigate(self, url: str) -> None: ...
    async def take_screenshot(self) -> bytes: ...
    async def click_element(self, selector: str) -> None: ...
    async def get_page_content(self) -> str: ...
    async def fill_form(self, form_data: Dict[str, str]) -> None: ...

# LEARNING CONCEPT 2: Rich Data Models with Validation
# Using dataclasses with type hints provides better IDE support,
# runtime validation, and automatic serialization
@dataclass
class Assignment:
    """Rich assignment model with validation and metadata"""
    title: str
    due_date: datetime
    course: str
    platform: str
    platform_id: str
    description: Optional[str] = None
    submission_method: Optional[str] = None
    points_possible: Optional[float] = None
    requirements: List[str] = None
    confidence_score: float = 0.0
    extraction_metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate data after initialization"""
        if self.requirements is None:
            self.requirements = []
        if self.extraction_metadata is None:
            self.extraction_metadata = {}
        if not 0 <= self.confidence_score <= 100:
            raise ValueError("Confidence score must be between 0 and 100")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['due_date'] = self.due_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Assignment':
        """Create from dictionary with type conversion"""
        if isinstance(data['due_date'], str):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        return cls(**data)

@dataclass
class Course:
    """Course information with enrollment status"""
    name: str
    code: str
    platform: str
    platform_id: str
    instructor: Optional[str] = None
    enrollment_status: str = "active"
    last_accessed: Optional[datetime] = None

class AgentCapability(Enum):
    """Enum for agent capabilities - helps with feature detection"""
    VISUAL_NAVIGATION = "visual_navigation"
    TEXT_PARSING = "text_parsing"
    FORM_FILLING = "form_filling"
    MEMORY_LEARNING = "memory_learning"
    API_INTEGRATION = "api_integration"

# LEARNING CONCEPT 3: Abstract Base Classes for Polymorphism
# This creates a contract that all LMS agents must follow
# Enables strategy pattern and dependency injection
class BaseLMSAgent(ABC):
    """
    Abstract base class for all LMS agents

    Teaching Concepts:
    - Abstract Base Classes (ABC) for interface definition
    - Strategy Pattern for interchangeable implementations
    - Dependency Injection for testability
    - Async/Await for concurrent operations
    """

    def __init__(self,
                 ai_client: AIClient,
                 browser_driver: BrowserDriver,
                 config: Dict[str, Any]):
        self.ai_client = ai_client
        self.browser = browser_driver
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._capabilities: List[AgentCapability] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        """Return list of supported capabilities"""
        return self._capabilities.copy()

    def supports_capability(self, capability: AgentCapability) -> bool:
        """Check if agent supports a specific capability"""
        return capability in self._capabilities

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the LMS platform"""
        pass

    @abstractmethod
    async def get_courses(self) -> List[Course]:
        """Fetch available courses"""
        pass

    @abstractmethod
    async def get_assignments(self, course_filters: List[str] = None) -> List[Assignment]:
        """Fetch assignments from the platform"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate that connection to platform is working"""
        pass

    # LEARNING CONCEPT 4: Template Method Pattern
    # This defines the algorithm structure while allowing subclasses
    # to override specific steps
    async def full_sync(self, credentials: Dict[str, str],
                       course_filters: List[str] = None) -> List[Assignment]:
        """
        Template method that defines the full sync process
        Subclasses can override individual steps while maintaining the flow
        """
        try:
            self.logger.info(f"Starting full sync for {self.__class__.__name__}")

            # Step 1: Authentication
            auth_success = await self.authenticate(credentials)
            if not auth_success:
                raise Exception("Authentication failed")

            # Step 2: Get available courses (optional filtering)
            courses = await self.get_courses()
            if course_filters:
                courses = [c for c in courses if c.code in course_filters or c.name in course_filters]

            # Step 3: Fetch assignments
            assignments = await self.get_assignments([c.code for c in courses])

            # Step 4: Post-process and validate
            validated_assignments = await self._post_process_assignments(assignments)

            self.logger.info(f"Sync completed: {len(validated_assignments)} assignments found")
            return validated_assignments

        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            raise

    async def _post_process_assignments(self, assignments: List[Assignment]) -> List[Assignment]:
        """Post-process assignments (validation, deduplication, etc.)"""
        processed = []

        for assignment in assignments:
            try:
                # Validate assignment data
                if not assignment.title or not assignment.due_date:
                    self.logger.warning(f"Skipping invalid assignment: {assignment}")
                    continue

                # Add platform metadata
                assignment.extraction_metadata.update({
                    'agent_type': self.__class__.__name__,
                    'extraction_time': datetime.now().isoformat(),
                    'platform_version': await self._detect_platform_version()
                })

                processed.append(assignment)

            except Exception as e:
                self.logger.warning(f"Error processing assignment {assignment.title}: {e}")
                continue

        return processed

    async def _detect_platform_version(self) -> str:
        """Detect platform version for compatibility tracking"""
        # This would be implemented by specific agents
        return "unknown"

# LEARNING CONCEPT 5: Factory Pattern for Agent Creation
# This allows dynamic creation of agents based on configuration
class AgentFactory:
    """
    Factory for creating LMS agents

    Teaching Concepts:
    - Factory Pattern for object creation
    - Registry Pattern for plugin management
    - Dependency Injection Container
    """

    _agents: Dict[str, type] = {}

    @classmethod
    def register_agent(cls, platform_name: str, agent_class: type):
        """Register a new agent type"""
        if not issubclass(agent_class, BaseLMSAgent):
            raise TypeError("Agent must inherit from BaseLMSAgent")
        cls._agents[platform_name] = agent_class

    @classmethod
    def create_agent(cls,
                    platform_name: str,
                    ai_client: AIClient,
                    browser_driver: BrowserDriver,
                    config: Dict[str, Any]) -> BaseLMSAgent:
        """Create an agent instance for the specified platform"""
        if platform_name not in cls._agents:
            raise ValueError(f"Unknown platform: {platform_name}")

        agent_class = cls._agents[platform_name]
        return agent_class(ai_client, browser_driver, config)

    @classmethod
    def get_available_platforms(cls) -> List[str]:
        """Get list of supported platforms"""
        return list(cls._agents.keys())

# LEARNING CONCEPT 6: Context Managers for Resource Management
# Ensures proper cleanup of browser resources and connections
class AgentSession:
    """
    Context manager for agent sessions

    Teaching Concepts:
    - Context Managers (__enter__/__exit__)
    - Resource management and cleanup
    - Exception handling in context managers
    """

    def __init__(self, agent: BaseLMSAgent):
        self.agent = agent
        self.start_time = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.start_time = datetime.now()
        self.agent.logger.info(f"Starting agent session: {self.agent.__class__.__name__}")

        # Initialize browser if needed
        if hasattr(self.agent.browser, 'initialize'):
            await self.agent.browser.initialize()

        return self.agent

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        duration = datetime.now() - self.start_time

        if exc_type:
            self.agent.logger.error(f"Session failed after {duration}: {exc_val}")
        else:
            self.agent.logger.info(f"Session completed successfully in {duration}")

        # Cleanup browser resources
        if hasattr(self.agent.browser, 'cleanup'):
            await self.agent.browser.cleanup()

        # Don't suppress exceptions
        return False

# LEARNING CONCEPT 7: Event-Driven Architecture
# This allows loose coupling between components
class AgentEvent:
    """Event data structure for agent operations"""
    def __init__(self, event_type: str, data: Dict[str, Any], agent_id: str):
        self.event_type = event_type
        self.data = data
        self.agent_id = agent_id
        self.timestamp = datetime.now()

class EventBus:
    """Simple event bus for agent communication"""
    def __init__(self):
        self._handlers: Dict[str, List[callable]] = {}

    def subscribe(self, event_type: str, handler: callable):
        """Subscribe to events of a specific type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: AgentEvent):
        """Publish an event to all subscribers"""
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")

# Example usage and testing
if __name__ == "__main__":
    # This demonstrates how the architecture would be used
    print("🧠 Universal LMS Agent Architecture")
    print("=" * 50)
    print()
    print("Key Concepts Demonstrated:")
    print("1. Protocol-Oriented Programming")
    print("2. Rich Data Models with Validation")
    print("3. Abstract Base Classes")
    print("4. Template Method Pattern")
    print("5. Factory Pattern")
    print("6. Context Managers")
    print("7. Event-Driven Architecture")
    print()
    print("This architecture enables:")
    print("✅ Easy addition of new platforms")
    print("✅ Consistent behavior across agents")
    print("✅ Proper resource management")
    print("✅ Type safety and validation")
    print("✅ Testable and maintainable code")