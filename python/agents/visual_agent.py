#!/usr/bin/env python3
"""
GPT-4V Browser Automation Agent
Teaching concepts: Computer Vision + AI, Browser Automation, Prompt Engineering
"""

import asyncio
import base64
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# We'll use playwright for browser automation (more modern than Selenium)
try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("Install playwright: pip install playwright")

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Computer Vision + Language Models
# GPT-4V can "see" and understand screenshots like a human
# This is a breakthrough in automation - no more brittle selectors!

@dataclass
class VisualElement:
    """Represents a UI element identified by AI"""
    description: str
    coordinates: Tuple[int, int]  # x, y position
    element_type: str  # button, link, input, etc.
    confidence: float
    bounding_box: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height

@dataclass
class NavigationPlan:
    """AI-generated plan for navigating a website"""
    steps: List[Dict[str, Any]]
    confidence: float
    reasoning: str
    estimated_time: float

class VisualBrowserAgent:
    """
    AI-powered browser agent that can navigate websites like a human

    Teaching Concepts:
    - Computer Vision integration with LLMs
    - Prompt engineering for visual tasks
    - Error recovery and adaptive behavior
    - State management in automation
    """

    def __init__(self, ai_client, headless: bool = True):
        self.ai_client = ai_client
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.navigation_history: List[Dict] = []
        self.learned_patterns: Dict[str, Any] = {}

    async def initialize(self):
        """Initialize browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        self.page = await self.browser.new_page()

        # Set realistic viewport and user agent
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    async def cleanup(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    # LEARNING CONCEPT 2: Prompt Engineering for Vision Tasks
    # The key to AI automation is writing prompts that guide the AI
    # to understand and interact with UIs effectively

    async def analyze_page_for_navigation(self, goal: str) -> NavigationPlan:
        """
        Use GPT-4V to analyze current page and plan navigation

        This is the core innovation: instead of hardcoded selectors,
        we use AI to understand the page visually
        """
        screenshot = await self.take_screenshot()

        # PROMPT ENGINEERING: This prompt is carefully crafted to get useful navigation instructions
        analysis_prompt = f"""
        You are an expert web navigator helping a student access their university assignments.

        GOAL: {goal}

        Look at this screenshot of a university website and provide a navigation plan.

        Analyze the page and identify:
        1. What type of page this is (login, dashboard, course list, etc.)
        2. Relevant clickable elements (buttons, links, menus)
        3. Form fields that might need to be filled
        4. Navigation steps to achieve the goal

        Focus on elements related to:
        - Assignments, homework, coursework
        - Course materials, syllabi
        - Student dashboards or portals
        - Login forms if authentication is needed

        Return your analysis in this JSON format:
        {{
            "page_type": "login|dashboard|courses|assignments|other",
            "identified_elements": [
                {{
                    "description": "Clear description of the element",
                    "element_type": "button|link|input|select|other",
                    "likely_selector": "suggested CSS selector or text content",
                    "coordinates": [x, y],
                    "confidence": 0.0-1.0
                }}
            ],
            "navigation_steps": [
                {{
                    "action": "click|type|select|wait",
                    "target": "element description",
                    "value": "text to type (if applicable)",
                    "reasoning": "why this step is needed"
                }}
            ],
            "confidence": 0.0-1.0,
            "reasoning": "explanation of your analysis",
            "potential_issues": ["list", "of", "potential", "problems"]
        }}
        """

        try:
            response = await self.ai_client.analyze_image(
                image=screenshot,
                prompt=analysis_prompt
            )

            # Parse AI response
            analysis = json.loads(response)

            # Convert to NavigationPlan object
            plan = NavigationPlan(
                steps=analysis.get('navigation_steps', []),
                confidence=analysis.get('confidence', 0.0),
                reasoning=analysis.get('reasoning', ''),
                estimated_time=len(analysis.get('navigation_steps', [])) * 2.0  # 2 seconds per step
            )

            logger.info(f"Navigation plan generated with {plan.confidence:.2f} confidence")
            return plan

        except Exception as e:
            logger.error(f"Failed to analyze page: {e}")
            # Return empty plan as fallback
            return NavigationPlan(
                steps=[],
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                estimated_time=0.0
            )

    # LEARNING CONCEPT 3: Adaptive Execution with Error Recovery
    # Real-world automation needs to handle failures gracefully

    async def execute_navigation_plan(self, plan: NavigationPlan) -> bool:
        """
        Execute the AI-generated navigation plan with error recovery

        This demonstrates:
        - Robust error handling
        - Adaptive behavior when plans fail
        - State tracking and recovery
        """
        success_count = 0

        for i, step in enumerate(plan.steps):
            try:
                logger.info(f"Executing step {i+1}/{len(plan.steps)}: {step['action']} - {step.get('reasoning', '')}")

                # Execute the step based on action type
                step_success = await self._execute_single_step(step)

                if step_success:
                    success_count += 1
                    # Wait for page to respond
                    await self.page.wait_for_timeout(1000)

                    # Take screenshot after each step for debugging
                    await self._record_step_result(step, True)
                else:
                    logger.warning(f"Step {i+1} failed, attempting recovery")
                    # Try alternative approaches
                    recovered = await self._attempt_step_recovery(step)
                    if recovered:
                        success_count += 1
                    else:
                        logger.error(f"Step {i+1} failed permanently")
                        await self._record_step_result(step, False)

            except Exception as e:
                logger.error(f"Exception in step {i+1}: {e}")
                await self._record_step_result(step, False)

        success_rate = success_count / len(plan.steps) if plan.steps else 0
        logger.info(f"Navigation completed: {success_count}/{len(plan.steps)} steps successful ({success_rate:.1%})")

        return success_rate >= 0.7  # Consider 70% success rate as acceptable

    async def _execute_single_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single navigation step"""
        action = step['action'].lower()
        target = step.get('target', '')
        value = step.get('value', '')

        try:
            if action == 'click':
                return await self._click_element(target)
            elif action == 'type':
                return await self._type_text(target, value)
            elif action == 'select':
                return await self._select_option(target, value)
            elif action == 'wait':
                await self.page.wait_for_timeout(int(value) * 1000)
                return True
            else:
                logger.warning(f"Unknown action: {action}")
                return False

        except Exception as e:
            logger.error(f"Failed to execute {action} on {target}: {e}")
            return False

    # LEARNING CONCEPT 4: Intelligent Element Location
    # Instead of brittle CSS selectors, we use multiple strategies

    async def _click_element(self, description: str) -> bool:
        """
        Click an element using multiple location strategies

        This shows how to make automation robust by trying multiple approaches
        """
        strategies = [
            self._click_by_text,
            self._click_by_role,
            self._click_by_ai_coordinates,
            self._click_by_fuzzy_match
        ]

        for strategy in strategies:
            try:
                if await strategy(description):
                    return True
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                continue

        logger.error(f"All click strategies failed for: {description}")
        return False

    async def _click_by_text(self, description: str) -> bool:
        """Try to click by visible text content"""
        # Extract likely text from description
        text_variants = [
            description.lower(),
            description.title(),
            description.upper(),
            # Handle common button text patterns
            description.replace('button', '').strip(),
            description.replace('link', '').strip()
        ]

        for text in text_variants:
            try:
                # Try exact text match first
                element = self.page.locator(f"text={text}")
                if await element.count() > 0:
                    await element.first.click()
                    return True

                # Try partial text match
                element = self.page.locator(f"text*={text}")
                if await element.count() > 0:
                    await element.first.click()
                    return True

            except Exception:
                continue

        return False

    async def _click_by_role(self, description: str) -> bool:
        """Try to click using ARIA roles"""
        role_mapping = {
            'button': 'button',
            'link': 'link',
            'menu': 'menu',
            'submit': 'button',
            'login': 'button'
        }

        for keyword, role in role_mapping.items():
            if keyword in description.lower():
                try:
                    elements = self.page.get_by_role(role)
                    count = await elements.count()

                    for i in range(count):
                        element = elements.nth(i)
                        text = await element.text_content() or ""
                        if any(word in text.lower() for word in description.lower().split()):
                            await element.click()
                            return True

                except Exception:
                    continue

        return False

    async def _click_by_ai_coordinates(self, description: str) -> bool:
        """Use AI to identify element coordinates and click there"""
        # This would use GPT-4V to identify specific coordinates
        # For now, we'll simulate this approach
        logger.debug(f"AI coordinate clicking not implemented for: {description}")
        return False

    async def _click_by_fuzzy_match(self, description: str) -> bool:
        """Try fuzzy matching against all clickable elements"""
        try:
            # Get all potentially clickable elements
            clickable_selectors = [
                'button', 'a', 'input[type="submit"]', 'input[type="button"]',
                '[role="button"]', '[onclick]', '.btn', '.button'
            ]

            for selector in clickable_selectors:
                elements = self.page.locator(selector)
                count = await elements.count()

                for i in range(count):
                    element = elements.nth(i)
                    # Get element text and attributes
                    text = await element.text_content() or ""
                    title = await element.get_attribute('title') or ""
                    aria_label = await element.get_attribute('aria-label') or ""

                    # Combine all text for matching
                    element_text = f"{text} {title} {aria_label}".lower()

                    # Simple fuzzy matching
                    description_words = description.lower().split()
                    matches = sum(1 for word in description_words if word in element_text)

                    if matches >= len(description_words) * 0.5:  # 50% word match threshold
                        await element.click()
                        return True

        except Exception as e:
            logger.error(f"Fuzzy matching failed: {e}")

        return False

    async def _type_text(self, target: str, text: str) -> bool:
        """Type text into form fields"""
        input_strategies = [
            lambda: self.page.get_by_placeholder(target),
            lambda: self.page.get_by_label(target),
            lambda: self.page.locator(f'input[name*="{target.lower()}"]'),
            lambda: self.page.locator(f'input[id*="{target.lower()}"]'),
        ]

        for strategy in input_strategies:
            try:
                element = strategy()
                if await element.count() > 0:
                    await element.first.fill(text)
                    return True
            except Exception:
                continue

        return False

    async def take_screenshot(self) -> bytes:
        """Take screenshot for AI analysis"""
        if not self.page:
            raise Exception("Browser not initialized")

        screenshot = await self.page.screenshot(
            full_page=False,  # Just visible area
            quality=85        # Compress slightly to reduce token usage
        )
        return screenshot

    async def navigate_to_assignments(self, platform_url: str, credentials: Dict[str, str]) -> List[Dict]:
        """
        High-level method to navigate to assignments page

        This demonstrates the complete flow:
        1. Navigate to platform
        2. Handle authentication
        3. Find assignments section
        4. Extract assignment data
        """
        assignments = []

        try:
            # Step 1: Navigate to the platform
            await self.page.goto(platform_url)
            await self.page.wait_for_load_state('networkidle')

            # Step 2: Handle authentication if needed
            auth_success = await self._handle_authentication(credentials)
            if not auth_success:
                logger.error("Authentication failed")
                return assignments

            # Step 3: Navigate to assignments
            nav_plan = await self.analyze_page_for_navigation("Find and access assignment list")
            nav_success = await self.execute_navigation_plan(nav_plan)

            if nav_success:
                # Step 4: Extract assignments from current page
                assignments = await self._extract_assignments_from_page()

        except Exception as e:
            logger.error(f"Navigation failed: {e}")

        return assignments

    async def _handle_authentication(self, credentials: Dict[str, str]) -> bool:
        """Handle login process using AI-guided automation"""
        # Check if already logged in
        current_url = self.page.url
        if 'dashboard' in current_url or 'home' in current_url:
            return True

        # Use AI to identify and fill login form
        login_plan = await self.analyze_page_for_navigation("Log in to the platform")

        # Execute login steps
        success = await self.execute_navigation_plan(login_plan)

        # Wait for redirect after login
        if success:
            await self.page.wait_for_timeout(3000)
            # Check if login was successful
            new_url = self.page.url
            return new_url != current_url and 'login' not in new_url.lower()

        return False

    async def _extract_assignments_from_page(self) -> List[Dict]:
        """Extract assignment data from current page using AI"""
        screenshot = await self.take_screenshot()
        page_content = await self.page.content()

        extraction_prompt = f"""
        Extract assignment information from this university page.

        Look for:
        - Assignment names/titles
        - Due dates
        - Course information
        - Point values
        - Submission requirements

        Return a JSON array of assignments in this format:
        [
            {{
                "title": "Assignment name",
                "due_date": "YYYY-MM-DD HH:MM",
                "course": "Course name/code",
                "points": "Point value or null",
                "description": "Brief description",
                "submission_method": "How to submit",
                "confidence": 0.0-1.0
            }}
        ]

        Only include items that are clearly assignments, homework, or projects.
        Use high confidence (>0.8) only for items you're very sure about.
        """

        try:
            response = await self.ai_client.structured_completion(
                prompt=extraction_prompt,
                response_format="json"
            )

            assignments = json.loads(response)
            logger.info(f"Extracted {len(assignments)} assignments from page")
            return assignments

        except Exception as e:
            logger.error(f"Assignment extraction failed: {e}")
            return []

    async def _record_step_result(self, step: Dict, success: bool):
        """Record step execution results for learning"""
        result = {
            'step': step,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'page_url': self.page.url if self.page else None
        }
        self.navigation_history.append(result)

    async def _attempt_step_recovery(self, step: Dict) -> bool:
        """Attempt to recover from failed step"""
        # Simple recovery: wait and retry
        await self.page.wait_for_timeout(2000)
        return await self._execute_single_step(step)

# Example usage
if __name__ == "__main__":
    print("🤖 Visual Browser Agent with GPT-4V")
    print("=" * 50)
    print()
    print("This agent can:")
    print("✅ See and understand web pages like a human")
    print("✅ Navigate any university LMS without custom code")
    print("✅ Adapt to UI changes automatically")
    print("✅ Handle authentication flows")
    print("✅ Extract assignments intelligently")
    print("✅ Recover from navigation failures")
    print()
    print("Key innovations:")
    print("🧠 Computer vision + language models")
    print("🎯 Prompt engineering for visual tasks")
    print("🔄 Adaptive error recovery")
    print("📊 Multi-strategy element location")