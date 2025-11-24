# Phase 5 Architecture: Gradescope Integration

## Overview

Add Gradescope integration using web scraping with Playwright since Gradescope has no public API. Automates login, fetches assignments, submissions, and grades.

## Architecture Components

### 1. Authentication Strategy

**Credential Storage:**
- Store email + password encrypted in Credential model
- No OAuth available (Gradescope doesn't support it)
- Users provide credentials directly

**Login Flow:**
1. User enters Gradescope email/password in frontend
2. Backend tests login with Playwright
3. If successful, encrypt and store credentials
4. Store session cookies for faster subsequent logins

**Security Considerations:**
- Encrypt credentials with Fernet
- Never log passwords
- Clear browser context after each scrape
- Use headless browser for security

### 2. Playwright Web Scraping

**Why Playwright:**
- Handles JavaScript-heavy sites (Gradescope is React-based)
- Supports headless mode for server environments
- Auto-waits for elements (better than Selenium)
- Browser context management
- Screenshot capability for debugging

**Browser Configuration:**
```python
browser = await playwright.chromium.launch(
    headless=True,
    args=['--no-sandbox', '--disable-dev-shm-usage']  # For Railway/Docker
)
```

**Scraping Strategy:**
1. Launch headless browser
2. Navigate to Gradescope login page
3. Fill email/password fields
4. Submit login form
5. Wait for dashboard to load
6. Navigate to courses list
7. For each course:
   - Navigate to assignments page
   - Scrape assignment list
   - For each assignment:
     - Get name, due date, points
     - Get submission status
     - Get grade (if available)
8. Parse and structure data
9. Close browser context

### 3. Data to Extract

**Courses:**
- Course name (e.g., "EECS 281")
- Course term (e.g., "Fall 2025")
- Course ID (from URL)
- Instructor name (if available)

**Assignments:**
- Assignment name
- Due date and time
- Points possible
- Assignment type (homework, exam, project)
- Submission status (submitted, not submitted, late)
- Grade/score (if graded)
- Submission time
- Gradescope URL (link to assignment)

**Grades:**
- Points earned
- Points possible
- Percentage
- Feedback/comments (if available)

### 4. Gradescope Service

**`backend/app/services/gradescope_service.py`:**

```python
class GradescopeService:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Launch browser and create context"""

    async def login(self) -> bool:
        """Login to Gradescope and verify success"""

    async def get_courses(self) -> List[Dict]:
        """Scrape list of courses"""

    async def get_course_assignments(self, course_id: str) -> List[Dict]:
        """Scrape assignments for a specific course"""

    async def parse_assignment(self, element) -> Dict:
        """Parse assignment data from DOM element"""

    async def close(self):
        """Close browser context"""
```

**Key Methods:**
- `test_connection()` - Verify login works
- `scrape_all_data()` - Main scraping orchestrator
- `get_courses()` - Scrape courses list
- `get_assignments()` - Scrape assignments for course
- Proper cleanup with async context managers

### 5. Backend API Endpoints

**POST `/api/v1/gradescope/connect`**
```python
Request:
{
  "email": "user@umich.edu",
  "password": "password123"
}

Response:
{
  "status": "success",
  "message": "Gradescope account connected"
}
```

**GET `/api/v1/gradescope/status`**
```python
Response:
{
  "connected": true,
  "email": "user@umich.edu",
  "last_synced": "2025-11-21T10:30:00Z",
  "last_sync_status": "success",
  "courses_count": 5,
  "assignments_count": 23
}
```

**POST `/api/v1/gradescope/sync`**
```python
Response:
{
  "status": "success",
  "message": "Successfully synced Gradescope data",
  "courses_found": 5,
  "courses_new": 2,
  "assignments_found": 23,
  "assignments_new": 15
}
```

**POST `/api/v1/gradescope/disconnect`**
```python
Response:
{
  "status": "success",
  "message": "Gradescope account disconnected"
}
```

### 6. Database Schema

Uses existing Phase 1 models:

**Credential:**
- `service = "gradescope"`
- `encrypted_data` = JSON with email, password
- `institution_url` = "https://www.gradescope.com"

**Course:**
- `source = "gradescope"`
- `source_id` = Gradescope course ID
- `source_url` = Link to course

**Assignment:**
- `source = "gradescope"`
- `source_id` = Gradescope assignment ID
- `source_url` = Link to assignment
- All grade fields populated

**ScrapeJob:**
- `service = "gradescope"`
- `job_type = "full_sync"`
- Tracks scraping performance

### 7. Frontend Components

**Settings Page:**
- Gradescope connection section
- Email/password form
- Connection status display
- Sync button

**Types:**
```typescript
interface GradescopeConnectRequest {
  email: string;
  password: string;
}

interface GradescopeStatus {
  connected: boolean;
  email?: string;
  last_synced?: string;
  last_sync_status?: string;
  courses_count?: number;
  assignments_count?: number;
}
```

### 8. Selectors Strategy

Gradescope DOM selectors (may change - need defensive coding):

**Login Page:**
```python
EMAIL_SELECTOR = 'input[name="email"]'
PASSWORD_SELECTOR = 'input[name="password"]'
SUBMIT_SELECTOR = 'button[type="submit"]'
```

**Dashboard:**
```python
COURSES_SELECTOR = '.courseList--coursesForTerm'
COURSE_NAME_SELECTOR = '.courseBox--shortname'
COURSE_TERM_SELECTOR = '.courseList--term-name'
```

**Assignments:**
```python
ASSIGNMENT_ROW_SELECTOR = '.table--assignments tbody tr'
ASSIGNMENT_NAME_SELECTOR = '.table--primaryLink'
DUE_DATE_SELECTOR = '.submissionTimeChart--dueDate'
POINTS_SELECTOR = '.assignment-score'
```

**Defensive Approach:**
- Try multiple selector strategies (CSS, XPath, text content)
- Graceful fallback if selectors fail
- Screenshot on error for debugging
- Detailed error logging

### 9. Error Handling

**Common Issues:**
- Login failures (wrong credentials)
- Selector changes (Gradescope updates UI)
- Network timeouts
- CAPTCHA challenges
- Rate limiting

**Solutions:**
- Retry logic with exponential backoff
- Screenshot capture on failures
- Detailed error messages
- Graceful degradation
- User notifications

### 10. Performance Optimization

**Challenges:**
- Web scraping is slow (each page load takes seconds)
- Multiple courses × assignments = many page loads
- Headless browser uses significant memory

**Optimizations:**
- Browser context reuse (don't relaunch for each scrape)
- Parallel scraping (multiple courses simultaneously)
- Aggressive timeouts (don't wait forever)
- Smart caching (only re-scrape if needed)
- Background jobs for large scrapes

**Typical Performance:**
- 5 courses, 25 assignments: ~30-60 seconds
- 10 courses, 100 assignments: ~2-5 minutes

### 11. Security Considerations

**Password Storage:**
- Encrypt with Fernet symmetric encryption
- Same encryption_service as Canvas/Gmail
- Never return passwords to frontend

**Browser Security:**
- Headless mode (no GUI)
- --no-sandbox flag for Docker/Railway
- Clear cookies/storage after each scrape
- No persistent browser data

**Rate Limiting:**
- Gradescope may block rapid requests
- Add delays between requests (100-500ms)
- Respect robots.txt (though scraping for personal use)

### 12. Gradescope DOM Structure

**Login Page:**
```html
<input name="email" type="email">
<input name="password" type="password">
<button type="submit">Log In</button>
```

**Courses Dashboard:**
```html
<div class="courseList--coursesForTerm">
  <div class="courseBox">
    <div class="courseBox--shortname">EECS 281</div>
    <div class="courseBox--name">Data Structures</div>
  </div>
</div>
```

**Assignments Page:**
```html
<table class="table--assignments">
  <tbody>
    <tr>
      <td><a class="table--primaryLink">Project 1</a></td>
      <td class="submissionTimeChart--dueDate">Nov 21, 11:59 PM</td>
      <td class="assignment-score">85 / 100</td>
    </tr>
  </tbody>
</table>
```

### 13. Implementation Plan

**Step 1: Backend - Gradescope Service**
- Install Playwright: `playwright install chromium`
- Create GradescopeService class
- Implement login flow
- Implement course scraping
- Implement assignment scraping
- Add error handling and retries

**Step 2: Backend - API Endpoints**
- Create gradescope.py router
- Implement /connect (test login, store credentials)
- Implement /status
- Implement /sync (orchestrate scraping)
- Implement /disconnect

**Step 3: Frontend - Gradescope UI**
- Add Gradescope types
- Create gradescope API client
- Add Gradescope section to Settings
- Email/password form
- Connection status display
- Sync button

**Step 4: Testing**
- Test with real Gradescope account
- Test error scenarios (wrong password)
- Test edge cases (no assignments, empty courses)
- Test performance with large datasets

**Step 5: Deployment**
- Ensure Playwright works on Railway
- Add Playwright install to deployment
- Test headless mode in production
- Monitor memory usage

### 14. Dependencies

**Backend:**
```
playwright==1.41.0  # Already in requirements.txt
```

**Playwright Installation:**
```bash
# Install Playwright browsers
playwright install chromium

# For Railway/Docker, add to Procfile or startup script
```

### 15. Railway Deployment Considerations

**Buildpack:**
- Railway may need custom buildpack for Playwright
- Chromium requires specific system dependencies

**Dockerfile Approach:**
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.41.0-focal
# Install dependencies
# Copy code
# Install Python packages
# Run app
```

**Environment:**
- Set `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`
- Ensure enough memory (512MB minimum)

### 16. Known Limitations

1. **No Real-time Updates**: Must manually sync
   - Gradescope has no webhooks
   - No way to get push notifications

2. **Scraping Fragility**: Breaks if Gradescope changes UI
   - Selectors may need updates
   - Requires maintenance

3. **Slow Performance**: Web scraping is inherently slow
   - Each page load takes seconds
   - Large courses take minutes to sync

4. **CAPTCHA Risk**: Gradescope may add CAPTCHA
   - Would break automated login
   - Need manual intervention

5. **No 2FA Support**: If user enables 2FA, scraping fails
   - Would need user to disable 2FA
   - Or store session cookies (risky)

### 17. Future Enhancements

**Phase 5.1:**
- Assignment file downloads (PDFs, specs)
- Submission history tracking
- Grade distribution stats

**Phase 5.2:**
- Smart caching (only scrape changed data)
- Incremental updates
- Background sync jobs with APScheduler

**Phase 5.3:**
- Gradescope notifications parsing
- Assignment comments/feedback
- Regrade request tracking

## Expected Outcomes

After Phase 5:
- ✅ Users can connect Gradescope with email/password
- ✅ Automatically sync courses and assignments
- ✅ Grades imported from Gradescope
- ✅ Deduplication with Canvas data
- ✅ Approval workflow for synced items
- ✅ Secure credential storage

## Success Metrics

- Login success rate: >95%
- Scraping accuracy: >90% (correct data extraction)
- Average sync time: <60 seconds for 5 courses
- Error recovery: Graceful failure handling
- User approval rate: >70% (useful data)
