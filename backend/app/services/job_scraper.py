"""
Job scraping service for LinkedIn, Indeed, and other job boards.
Uses Playwright for JavaScript-heavy sites.
"""
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import asyncio
from datetime import datetime, timedelta
import re


class JobScraper:
    """Scrape job listings from multiple sources."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        """Initialize Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        return self

    async def __aexit__(self, *args):
        """Cleanup browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_linkedin(
        self,
        keywords: str,
        location: str = "",
        job_type: str = "I",  # I=Internship, F=Full-time, P=Part-time
        limit: int = 25
    ) -> List[Dict]:
        """
        Scrape LinkedIn jobs (public listings only, no login required).

        Args:
            keywords: Job search keywords (e.g., "Software Engineer")
            location: Location (e.g., "New York, NY" or "Remote")
            job_type: Job type code (I=Internship, F=Full-time, P=Part-time)
            limit: Max number of jobs to scrape

        Returns:
            List of job dictionaries
        """
        page = await self.context.new_page()
        jobs = []

        try:
            # Build LinkedIn Jobs search URL (public API, no auth required)
            base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            params = {
                'keywords': keywords,
                'location': location,
                'f_E': job_type,  # Experience level
                'f_TPR': 'r86400',  # Posted in last 24 hours
                'start': 0
            }

            # LinkedIn paginates in groups of 25
            for offset in range(0, limit, 25):
                params['start'] = offset
                url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])

                await page.goto(url, wait_until='domcontentloaded')
                await asyncio.sleep(2)  # Be respectful

                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')

                # Parse job cards
                job_cards = soup.find_all('li')

                if not job_cards:
                    break  # No more jobs

                for card in job_cards:
                    try:
                        job = self._parse_linkedin_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error parsing LinkedIn job card: {e}")
                        continue

                if len(jobs) >= limit:
                    break

        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
        finally:
            await page.close()

        return jobs[:limit]

    def _parse_linkedin_card(self, card: BeautifulSoup) -> Optional[Dict]:
        """Parse a LinkedIn job card."""
        try:
            # Extract job URL and ID
            link = card.find('a', class_='base-card__full-link')
            if not link:
                return None

            job_url = link.get('href', '')
            job_id = self._extract_job_id_from_url(job_url)

            # Extract title
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.text.strip() if title_elem else "Unknown"

            # Extract company
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.text.strip() if company_elem else "Unknown"

            # Extract location
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.text.strip() if location_elem else "Unknown"

            # Extract posted date
            time_elem = card.find('time')
            posted_date = self._parse_relative_date(time_elem.get('datetime')) if time_elem else None

            return {
                'external_id': f"linkedin_{job_id}",
                'source': 'linkedin',
                'title': title,
                'company': company,
                'location': location,
                'application_url': job_url,
                'application_method': 'external',  # Requires LinkedIn login for Easy Apply
                'posted_date': posted_date,
                'description': None,  # Need to scrape individual job page for this
                'requirements': None,
            }

        except Exception as e:
            print(f"Error parsing card: {e}")
            return None

    async def scrape_indeed(
        self,
        keywords: str,
        location: str = "",
        job_type: str = "internship",
        limit: int = 25
    ) -> List[Dict]:
        """
        Scrape Indeed jobs.

        Args:
            keywords: Job search keywords
            location: Location
            job_type: "internship", "fulltime", "parttime"
            limit: Max number of jobs

        Returns:
            List of job dictionaries
        """
        page = await self.context.new_page()
        jobs = []

        try:
            # Build Indeed search URL
            base_url = "https://www.indeed.com/jobs"
            params = {
                'q': keywords,
                'l': location,
                'jt': job_type,
                'sort': 'date',
            }

            url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])

            await page.goto(url, wait_until='domcontentloaded')
            await asyncio.sleep(2)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Find job cards (Indeed uses different classes periodically, so try multiple)
            job_cards = soup.find_all('div', class_=re.compile(r'job_seen_beacon|jobsearch-ResultsList'))

            for card in job_cards[:limit]:
                try:
                    job = self._parse_indeed_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    print(f"Error parsing Indeed card: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping Indeed: {e}")
        finally:
            await page.close()

        return jobs[:limit]

    def _parse_indeed_card(self, card: BeautifulSoup) -> Optional[Dict]:
        """Parse an Indeed job card."""
        try:
            # Extract title and link
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                return None

            link = title_elem.find('a')
            if not link:
                return None

            title = title_elem.text.strip()
            job_url = "https://www.indeed.com" + link.get('href', '')
            job_id = self._extract_job_id_from_url(job_url)

            # Extract company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = company_elem.text.strip() if company_elem else "Unknown"

            # Extract location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            location = location_elem.text.strip() if location_elem else "Unknown"

            # Extract salary if available
            salary_elem = card.find('div', class_='salary-snippet')
            salary_text = salary_elem.text.strip() if salary_elem else None
            salary_min, salary_max = self._parse_salary(salary_text) if salary_text else (None, None)

            return {
                'external_id': f"indeed_{job_id}",
                'source': 'indeed',
                'title': title,
                'company': company,
                'location': location,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'application_url': job_url,
                'application_method': 'external',
                'posted_date': datetime.now(),  # Indeed doesn't always show date on cards
                'description': None,
                'requirements': None,
            }

        except Exception as e:
            print(f"Error parsing card: {e}")
            return None

    async def scrape_job_details(self, job_url: str, source: str) -> Dict:
        """
        Scrape full job details from individual job page.

        Args:
            job_url: URL of the job posting
            source: "linkedin" or "indeed"

        Returns:
            Dictionary with description, requirements, benefits, etc.
        """
        page = await self.context.new_page()
        details = {}

        try:
            await page.goto(job_url, wait_until='domcontentloaded')
            await asyncio.sleep(2)

            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            if source == 'linkedin':
                details = self._parse_linkedin_details(soup)
            elif source == 'indeed':
                details = self._parse_indeed_details(soup)

        except Exception as e:
            print(f"Error scraping job details: {e}")
        finally:
            await page.close()

        return details

    def _parse_linkedin_details(self, soup: BeautifulSoup) -> Dict:
        """Parse full LinkedIn job posting details."""
        # Job description
        desc_elem = soup.find('div', class_='description__text')
        description = desc_elem.text.strip() if desc_elem else ""

        # Extract skills if listed
        skills = []
        skill_elems = soup.find_all('span', class_='job-criteria-text')
        for elem in skill_elems:
            skills.append(elem.text.strip())

        return {
            'description': description,
            'requirements': description,  # LinkedIn doesn't separate these
            'required_skills': skills,
        }

    def _parse_indeed_details(self, soup: BeautifulSoup) -> Dict:
        """Parse full Indeed job posting details."""
        # Job description
        desc_elem = soup.find('div', id='jobDescriptionText')
        description = desc_elem.text.strip() if desc_elem else ""

        return {
            'description': description,
            'requirements': description,
        }

    # Helper methods

    def _extract_job_id_from_url(self, url: str) -> str:
        """Extract job ID from URL."""
        # Try to find numeric ID in URL
        matches = re.findall(r'[0-9]{10,}', url)
        return matches[0] if matches else url.split('/')[-1]

    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative date strings like '2 days ago' or ISO dates."""
        if not date_str:
            return None

        try:
            # Try parsing as ISO date
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass

        # Parse relative dates
        if 'hour' in date_str or 'hours' in date_str:
            hours = int(re.findall(r'\d+', date_str)[0])
            return datetime.now() - timedelta(hours=hours)
        elif 'day' in date_str or 'days' in date_str:
            days = int(re.findall(r'\d+', date_str)[0])
            return datetime.now() - timedelta(days=days)
        elif 'week' in date_str or 'weeks' in date_str:
            weeks = int(re.findall(r'\d+', date_str)[0])
            return datetime.now() - timedelta(weeks=weeks)

        return None

    def _parse_salary(self, salary_text: str) -> tuple[Optional[int], Optional[int]]:
        """Parse salary range from text like '$50,000 - $70,000 a year'."""
        if not salary_text:
            return None, None

        # Extract numbers
        numbers = re.findall(r'[\d,]+', salary_text)
        if not numbers:
            return None, None

        # Convert to integers
        salaries = [int(n.replace(',', '')) for n in numbers]

        if len(salaries) == 1:
            return salaries[0], salaries[0]
        elif len(salaries) >= 2:
            return min(salaries), max(salaries)

        return None, None


# Convenience function for API
async def scrape_jobs_for_user(
    keywords: List[str],
    locations: List[str],
    job_type: str = "internship",
    max_per_search: int = 10
) -> List[Dict]:
    """
    Scrape jobs for user preferences.

    Args:
        keywords: List of job titles/keywords to search
        locations: List of locations to search
        job_type: Type of job
        max_per_search: Max jobs per keyword/location combo

    Returns:
        Combined list of jobs from all sources
    """
    all_jobs = []

    async with JobScraper() as scraper:
        for keyword in keywords:
            for location in locations:
                # Scrape LinkedIn
                linkedin_jobs = await scraper.scrape_linkedin(
                    keywords=keyword,
                    location=location,
                    job_type='I' if job_type == 'internship' else 'F',
                    limit=max_per_search
                )
                all_jobs.extend(linkedin_jobs)

                # Scrape Indeed
                indeed_jobs = await scraper.scrape_indeed(
                    keywords=keyword,
                    location=location,
                    job_type=job_type,
                    limit=max_per_search
                )
                all_jobs.extend(indeed_jobs)

                # Be respectful with rate limiting
                await asyncio.sleep(5)

    # Deduplicate by external_id
    seen_ids = set()
    unique_jobs = []
    for job in all_jobs:
        if job['external_id'] not in seen_ids:
            seen_ids.add(job['external_id'])
            unique_jobs.append(job)

    return unique_jobs
