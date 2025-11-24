"""
LinkedIn job scraping service using Playwright.
Users provide LinkedIn job search URLs, we scrape listings.
"""
from typing import List, Dict, Optional
from datetime import datetime
import re
import asyncio

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout


class LinkedInService:
    """Service for scraping LinkedIn job listings."""

    BASE_URL = "https://www.linkedin.com"

    def __init__(self):
        """Initialize LinkedIn service."""
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

        # Launch headless browser
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
            ]
        )

        # Create browser context with realistic settings
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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

    async def scrape_job_search(self, search_url: str, max_jobs: int = 25) -> List[Dict]:
        """
        Scrape job listings from LinkedIn search URL.

        Args:
            search_url: LinkedIn job search URL
            max_jobs: Maximum number of jobs to scrape

        Returns:
            List of job dictionaries
        """
        try:
            # Navigate to search URL
            await self.page.goto(search_url, wait_until='networkidle', timeout=30000)

            # Wait for job listings to load
            await asyncio.sleep(2)

            jobs = []

            # Find all job cards
            job_cards = await self.page.query_selector_all('.job-search-card, .base-card')

            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    job_data = await self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)

                    # Small delay between parsing
                    await asyncio.sleep(0.3)

                except Exception as e:
                    print(f"Error parsing job card {i}: {e}")
                    continue

            return jobs

        except Exception as e:
            print(f"Error scraping LinkedIn jobs: {e}")
            return []

    async def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse job data from job card element."""
        try:
            # Get job title
            title_elem = await card.query_selector('.base-search-card__title, .job-search-card__title')
            if not title_elem:
                return None
            title = await title_elem.text_content()
            title = title.strip() if title else None

            # Get company name
            company_elem = await card.query_selector('.base-search-card__subtitle, .job-search-card__company-name')
            company = None
            if company_elem:
                company_text = await company_elem.text_content()
                company = company_text.strip() if company_text else None

            # Get location
            location_elem = await card.query_selector('.job-search-card__location, .job-search-card-location')
            location = None
            if location_elem:
                location_text = await location_elem.text_content()
                location = location_text.strip() if location_text else None

            # Get job URL
            link_elem = await card.query_selector('a.base-card__full-link, a')
            job_url = None
            if link_elem:
                job_url = await link_elem.get_attribute('href')
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.BASE_URL}{job_url}"

            # Get posted date (if available)
            posted_elem = await card.query_selector('.job-search-card__listdate, time')
            posted_date = None
            if posted_elem:
                posted_text = await posted_elem.text_content()
                posted_date = self._parse_posted_date(posted_text)

            # Get snippet/description
            snippet_elem = await card.query_selector('.job-search-card__snippet, .base-search-card__snippet')
            snippet = None
            if snippet_elem:
                snippet_text = await snippet_elem.text_content()
                snippet = snippet_text.strip() if snippet_text else None

            if not title:
                return None

            return {
                'title': title,
                'company': company or 'Unknown Company',
                'location': location or 'Location not specified',
                'job_url': job_url,
                'snippet': snippet,
                'posted_date': posted_date,
            }

        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def _parse_posted_date(self, date_text: str) -> Optional[datetime]:
        """Parse posted date from text like '2 days ago', '1 week ago'."""
        if not date_text:
            return None

        try:
            date_text = date_text.strip().lower()
            now = datetime.utcnow()

            # Handle "X days ago"
            if 'day' in date_text:
                match = re.search(r'(\d+)', date_text)
                if match:
                    days = int(match.group(1))
                    from datetime import timedelta
                    return now - timedelta(days=days)

            # Handle "X weeks ago"
            elif 'week' in date_text:
                match = re.search(r'(\d+)', date_text)
                if match:
                    weeks = int(match.group(1))
                    from datetime import timedelta
                    return now - timedelta(weeks=weeks)

            # Handle "X months ago"
            elif 'month' in date_text:
                match = re.search(r'(\d+)', date_text)
                if match:
                    months = int(match.group(1))
                    from datetime import timedelta
                    return now - timedelta(days=months * 30)

            # Default to now
            return now

        except Exception:
            return datetime.utcnow()

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skill keywords from job description/requirements.

        Args:
            text: Job description or requirements text

        Returns:
            List of matched skills
        """
        if not text:
            return []

        text_lower = text.lower()

        # Common tech skills to look for
        tech_skills = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "ruby", "php", "swift", "kotlin", "r", "matlab", "scala",

            # Web Technologies
            "react", "angular", "vue", "node.js", "express", "django", "flask",
            "spring", "asp.net", "html", "css", "sass", "webpack",

            # Databases
            "sql", "postgresql", "mysql", "mongodb", "redis", "cassandra",
            "dynamodb", "elasticsearch",

            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
            "terraform", "ansible", "ci/cd", "git", "github", "gitlab",

            # Data & ML
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
            "machine learning", "deep learning", "data science", "nlp",
            "computer vision", "spark", "hadoop",

            # Mobile
            "ios", "android", "react native", "flutter",

            # Other
            "rest api", "graphql", "microservices", "agile", "scrum",
            "linux", "bash", "testing", "unit testing", "tdd",
        ]

        found_skills = []
        for skill in tech_skills:
            if skill in text_lower:
                # Capitalize properly
                found_skills.append(skill.title())

        return list(set(found_skills))  # Remove duplicates

    def infer_job_type(self, title: str, description: str = None) -> str:
        """
        Infer job type from title and description.

        Returns:
            "internship", "full-time", "part-time", "contract"
        """
        text = (title + " " + (description or "")).lower()

        if any(word in text for word in ['intern', 'internship', 'co-op']):
            return 'internship'
        elif any(word in text for word in ['part-time', 'part time', 'hourly']):
            return 'part-time'
        elif any(word in text for word in ['contract', 'contractor', 'freelance']):
            return 'contract'
        else:
            return 'full-time'

    def infer_remote_type(self, location: str, description: str = None) -> str:
        """
        Infer remote type from location and description.

        Returns:
            "remote", "hybrid", "onsite"
        """
        text = (location + " " + (description or "")).lower()

        if any(word in text for word in ['remote', 'work from home', 'wfh']):
            return 'remote'
        elif any(word in text for word in ['hybrid']):
            return 'hybrid'
        else:
            return 'onsite'

    def parse_salary(self, text: str) -> tuple[Optional[float], Optional[float]]:
        """
        Parse salary from text like "$80K - $100K" or "$50/hour".

        Returns:
            Tuple of (min_salary, max_salary) in dollars
        """
        if not text:
            return None, None

        try:
            # Look for patterns like $80K-$100K or $80,000-$100,000
            match = re.search(r'\$?([\d,]+)k?\s*-\s*\$?([\d,]+)k?', text, re.IGNORECASE)
            if match:
                min_sal = float(match.group(1).replace(',', ''))
                max_sal = float(match.group(2).replace(',', ''))

                # If values are like 80 (meaning 80K), multiply by 1000
                if min_sal < 1000:
                    min_sal *= 1000
                if max_sal < 1000:
                    max_sal *= 1000

                return min_sal, max_sal

            # Look for single salary like $80K
            match = re.search(r'\$?([\d,]+)k?', text, re.IGNORECASE)
            if match:
                salary = float(match.group(1).replace(',', ''))
                if salary < 1000:
                    salary *= 1000
                return salary, salary

        except Exception as e:
            print(f"Error parsing salary: {e}")

        return None, None
