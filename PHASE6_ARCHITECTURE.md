# Phase 6 Architecture: LinkedIn Job Scraping

## Overview

Add LinkedIn job aggregation using web scraping. MVP approach: users provide LinkedIn job search URLs, system scrapes listings, calculates match scores based on courses/skills.

## Architecture Components

### 1. MVP Approach: Manual URL Entry

**Why Manual URLs:**
- LinkedIn actively blocks automated scraping
- LinkedIn API requires company partnership (not available)
- Manual URL entry is legal and user-controlled
- Users paste LinkedIn job search URLs into our system

**User Flow:**
1. User searches for jobs on LinkedIn (e.g., "Software Engineer intern")
2. User copies the LinkedIn search URL
3. User pastes URL into our app
4. System scrapes job listings from that URL
5. System calculates match scores
6. User sees ranked job recommendations

### 2. LinkedIn Scraping Strategy

**URL Format:**
```
https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=Ann%20Arbor
```

**Scraping Method:**
- Use Playwright (same as Gradescope)
- Headless browser with realistic user agent
- Scrape without login (public job listings)
- Extract: title, company, location, description, salary, posted date

**Anti-Bot Considerations:**
- Delays between requests (1-2 seconds)
- Realistic user agent strings
- Don't scrape too aggressively
- Respect rate limits
- Only scrape public listings

### 3. Data to Extract

**Job Listings:**
- Job title
- Company name
- Location (city, state)
- Remote type (remote, hybrid, onsite)
- Job type (internship, full-time, part-time)
- Description (full text)
- Requirements/qualifications
- Salary range (if available)
- Application URL
- Posted date
- Source (always "linkedin")

**From Job Description:**
- Required skills (parse text for keywords)
- Preferred qualifications
- Experience level
- Education requirements

### 4. Match Scoring Algorithm

**Inputs:**
- User's courses (from Canvas/Gradescope)
- User's skills (extracted from assignments/projects)
- Job requirements (from description)

**Scoring Factors:**
```python
score = (
    skill_match_score * 0.4 +      # 40%: Skills match
    course_relevance_score * 0.3 +  # 30%: Course relevance
    location_score * 0.15 +         # 15%: Location preference
    recency_score * 0.15            # 15%: How recently posted
)
```

**Skill Matching:**
- Extract keywords from job description (Python, React, SQL, etc.)
- Match against user's course list (EECS 281 → "Data Structures", "C++")
- Match against assignment titles/descriptions
- Calculate overlap percentage

**Course Relevance:**
- Map courses to job domains:
  - EECS 281/482/485 → Software Engineering
  - EECS 445 → Machine Learning
  - EECS 370 → Computer Architecture
- Score based on domain alignment

### 5. LinkedIn Service

**`backend/app/services/linkedin_service.py`:**

```python
class LinkedInService:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def scrape_job_search(self, search_url: str) -> List[Dict]:
        """Scrape jobs from LinkedIn search URL"""

    async def parse_job_card(self, element) -> Dict:
        """Parse individual job listing"""

    async def get_job_details(self, job_url: str) -> Dict:
        """Get full job details (optional deep scrape)"""

    def extract_skills(self, description: str) -> List[str]:
        """Extract skill keywords from job description"""
```

**Job Matching Service:**

```python
class JobMatchingService:
    def __init__(self, user_id: int, db: AsyncSession):
        self.user_id = user_id
        self.db = db

    async def get_user_profile(self) -> Dict:
        """Build user profile from courses/assignments"""

    async def calculate_match_score(self, job: JobListing) -> float:
        """Calculate match score for a job"""

    def skill_match_score(self, job_skills: List[str], user_skills: List[str]) -> float:
        """Calculate skill overlap score"""

    def course_relevance_score(self, job: JobListing, user_courses: List[Course]) -> float:
        """Calculate course relevance score"""
```

### 6. Backend API Endpoints

**POST `/api/v1/jobs/scrape`**
```python
Request:
{
  "search_url": "https://www.linkedin.com/jobs/search/?keywords=...",
  "location_preference": "Ann Arbor, MI"  # Optional
}

Response:
{
  "status": "success",
  "jobs_found": 25,
  "jobs_new": 20,
  "message": "Successfully scraped 25 job listings"
}
```

**GET `/api/v1/jobs`**
```python
# Get all jobs, sorted by match score
Response: [
  {
    "id": 1,
    "title": "Software Engineering Intern",
    "company": "Microsoft",
    "location": "Redmond, WA",
    "remote_type": "hybrid",
    "match_score": 0.85,
    "matched_skills": ["Python", "React", "SQL"],
    "application_url": "https://...",
    ...
  }
]
```

**GET `/api/v1/jobs/{job_id}`**
```python
# Get single job details
```

**GET `/api/v1/jobs/{job_id}/match`**
```python
# Get detailed match breakdown
Response:
{
  "match_score": 0.85,
  "skill_match": 0.90,
  "course_relevance": 0.75,
  "location_match": 1.0,
  "match_reasons": [
    "Your EECS 281 course matches 'Data Structures' requirement",
    "You have experience with Python from 5 assignments",
    "Location matches your preference"
  ],
  "missing_skills": ["AWS", "Docker"]
}
```

**POST `/api/v1/jobs/{job_id}/apply`**
```python
# Mark job as applied
Request:
{
  "applied_date": "2025-11-21",
  "notes": "Submitted via LinkedIn"
}

Response:
{
  "status": "success",
  "job_match": {...}
}
```

**PUT `/api/v1/jobs/matches/{match_id}`**
```python
# Update application status
Request:
{
  "status": "interviewing",
  "notes": "Phone interview scheduled for Monday"
}
```

### 7. Database Schema

Uses existing Phase 1 models:

**JobListing:**
```python
# Already exists in models/job_listing.py
title, company, location, remote_type, job_type
description, requirements, qualifications
salary_min, salary_max
application_url, source, posted_date
skills (JSON array)
```

**JobMatch:**
```python
# Already exists in models/job_match.py
job_id, user_id
match_score (0-100)
skill_match_score, course_relevance_score, location_score
matched_skills (JSON array)
match_reasons (JSON array)
missing_skills (JSON array)
status (saved, applied, interviewing, offer, rejected)
applied_date, notes
```

### 8. Frontend Components

**Jobs Page (`/jobs`):**
- Job search URL input
- "Scrape Jobs" button
- Job list with match scores
- Filters (remote type, job type, location)
- Sort by match score, posted date, salary

**Job Card Component:**
- Match score badge (color-coded: >80% green, 60-80% yellow, <60% gray)
- Job title, company, location
- Remote badge, job type badge
- Matched skills chips
- "View Details" and "Mark as Applied" buttons

**Job Details Modal:**
- Full description
- Detailed match breakdown
- Match reasons
- Missing skills
- Application tracking
- Notes field

**My Applications View:**
- Filter by status (applied, interviewing, offer, rejected)
- Timeline of application progress
- Notes for each application

### 9. LinkedIn Selectors

**Job Search Page:**
```python
JOB_CARD_SELECTOR = '.job-search-card, .jobs-search__results-list li'
JOB_TITLE_SELECTOR = '.job-search-card__title, .base-search-card__title'
COMPANY_SELECTOR = '.job-search-card__company-name, .base-search-card__subtitle'
LOCATION_SELECTOR = '.job-search-card__location'
```

**Defensive Approach:**
- Multiple selector strategies
- Graceful fallback on failures
- Screenshot on error
- Detailed logging

### 10. Skill Extraction

**Common Tech Skills:**
```python
TECH_SKILLS = [
    # Languages
    "Python", "Java", "JavaScript", "C++", "C", "Go", "Rust", "TypeScript",
    # Web
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Express",
    # Data
    "SQL", "PostgreSQL", "MongoDB", "Redis", "MySQL",
    # Cloud/DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git",
    # ML/AI
    "TensorFlow", "PyTorch", "scikit-learn", "Machine Learning", "Deep Learning",
    # Other
    "REST API", "GraphQL", "Microservices", "Agile", "CI/CD"
]
```

**Extraction Method:**
- Case-insensitive keyword matching
- Tokenize job description
- Match against skill database
- Return unique skills found

### 11. Performance Optimization

**Scraping:**
- Async Playwright for concurrent scraping
- Cache job listings (don't re-scrape same URL within 24 hours)
- Background jobs for large scrapes (APScheduler)

**Match Scoring:**
- Cache user profile (courses, skills)
- Batch calculate scores for all jobs
- Index jobs by match score

### 12. Error Handling

**Common Issues:**
- LinkedIn blocks (CAPTCHA, rate limiting)
- Invalid URLs
- Selector changes
- Network timeouts

**Solutions:**
- Retry with exponential backoff
- User-friendly error messages
- Fallback to manual entry
- Cache successful scrapes

### 13. Implementation Plan

**Step 1: Backend - LinkedIn Service**
- Create LinkedInService with Playwright
- Implement job search scraping
- Parse job cards
- Extract skills from descriptions

**Step 2: Backend - Job Matching**
- Create JobMatchingService
- Build user profile from courses
- Implement match scoring algorithm
- Calculate skill overlap

**Step 3: Backend - API Endpoints**
- Create jobs.py router
- Implement /scrape (trigger scraping)
- Implement /jobs (list with scores)
- Implement /jobs/{id}/match (detailed match)
- Implement application tracking endpoints

**Step 4: Frontend - Jobs UI**
- Create Jobs page
- URL input and scrape button
- Job list with match scores
- Job details modal
- Application tracking

**Step 5: Testing**
- Test with real LinkedIn URLs
- Verify match scoring accuracy
- Test application tracking
- Test error scenarios

### 14. Legal/Ethical Considerations

**LinkedIn Terms of Service:**
- We're scraping PUBLIC job listings
- Users provide URLs (user-initiated)
- No automated bulk scraping
- Respecting robots.txt
- Adding delays between requests

**Best Practices:**
- Only scrape when user requests
- Cache results to minimize requests
- Clear attribution (source: LinkedIn)
- Don't resell or redistribute data
- For personal educational use only

### 15. Known Limitations

1. **No Auto-Refresh**: Must manually re-scrape URLs
   - No real-time job alerts
   - Jobs may become outdated

2. **LinkedIn Anti-Bot**: May get blocked
   - CAPTCHA challenges
   - IP bans for aggressive scraping
   - Need conservative rate limiting

3. **Scraping Fragility**: Breaks if LinkedIn changes
   - Selectors may need updates
   - Requires maintenance

4. **Limited Data**: Only public info
   - Can't access full details without login
   - Salary often not shown
   - Application count not available

5. **No Application Integration**: Can't apply through our app
   - Users redirected to LinkedIn
   - Manual tracking only

### 16. Future Enhancements

**Phase 6.1:**
- Indeed, Glassdoor scraping
- Multi-source job aggregation
- Deduplication across sources

**Phase 6.2:**
- AI-powered resume matching
- Cover letter generation
- Interview prep suggestions

**Phase 6.3:**
- Application deadline tracking
- Email reminders for followups
- Application analytics

**Phase 6.4:**
- Company research integration
- Salary insights
- Interview reviews (Glassdoor)

## Expected Outcomes

After Phase 6:
- ✅ Users can scrape LinkedIn job listings
- ✅ Jobs ranked by match score
- ✅ Skill-based matching
- ✅ Application tracking
- ✅ Career recommendations

## Success Metrics

- Scraping success rate: >90%
- Match accuracy (user feedback): >75% relevant
- Average match score for applied jobs: >70%
- Application tracking adoption: >50% of users

---

This completes the 4 major integrations (Canvas, Gmail, Gradescope, LinkedIn) and provides a comprehensive student hub platform!
