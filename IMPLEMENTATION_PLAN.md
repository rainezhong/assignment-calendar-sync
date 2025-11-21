# Student Hub - Implementation Plan

**Current Status:** Working FastAPI backend with assignments, career features, AI intelligence deployed on Railway.

**Goal:** Add web scraping integrations, React frontend, and approval workflows to create a unified academic & career dashboard.

---

## Phase 1: Database Schema Extensions (Week 1)

### 1.1 New Models to Add

#### Courses Model
```python
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Course info
    name = Column(String, nullable=False)  # "Database Systems"
    code = Column(String)  # "CS 440"
    semester = Column(String)  # "Fall 2025"
    instructor = Column(String)

    # Integration tracking
    source = Column(String)  # "canvas", "gradescope", "manual"
    source_id = Column(String, index=True)  # ID in source system
    source_url = Column(String)

    # Approval
    approved = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    last_synced = Column(DateTime)
```

#### Credentials Model (Encrypted)
```python
class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    service = Column(String)  # "canvas", "gradescope", "gmail"
    encrypted_data = Column(Text)  # Encrypted JSON with credentials

    is_active = Column(Boolean, default=True)
    last_synced = Column(DateTime)
    last_error = Column(String)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint('user_id', 'service'),)
```

#### Emails Model
```python
class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Email details
    subject = Column(String)
    sender = Column(String)
    sender_email = Column(String)
    body = Column(Text)
    html_body = Column(Text)

    # Gmail specific
    gmail_message_id = Column(String, unique=True, index=True)
    gmail_thread_id = Column(String)

    # Classification
    is_academic = Column(Boolean, default=False)
    category = Column(String)  # "assignment", "grade", "announcement", "other"

    # Relations
    related_course_id = Column(Integer, ForeignKey("courses.id"))
    related_assignment_id = Column(Integer, ForeignKey("assignments.id"))

    # Approval
    approved = Column(Boolean, default=False)

    # Timestamps
    received_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
```

#### ScrapeJob Model
```python
class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    service = Column(String)  # "canvas", "gradescope", "gmail"
    status = Column(String)  # "pending", "running", "completed", "failed"

    # Results
    items_found = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)

    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    created_at = Column(DateTime, server_default=func.now())
```

### 1.2 Extend Existing Models

**Assignment model - add these fields:**
```python
# Integration tracking
source = Column(String)  # "canvas", "gradescope", "gmail", "manual"
source_id = Column(String, index=True)  # External ID
source_url = Column(String)  # Link to original

# Approval
approved = Column(Boolean, default=False)
approved_at = Column(DateTime)

# Grading (from Canvas/Gradescope)
points_possible = Column(Float)
points_earned = Column(Float)
grade_percentage = Column(Float)
submission_status = Column(String)  # "submitted", "graded", "late", "missing"
```

### 1.3 Create Alembic Migration

```bash
cd backend
alembic revision --autogenerate -m "Add courses, credentials, emails, scrape_jobs tables"
alembic upgrade head
```

---

## Phase 2: React Frontend Setup (Week 1-2)

### 2.1 Initialize Frontend

```bash
cd /Users/raine/assignment-calendar-sync
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

# Install dependencies
npm install react-router-dom @tanstack/react-query axios
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react  # Icons
npm install date-fns  # Date formatting
npm install zustand  # State management
```

### 2.2 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── DashboardLayout.tsx
│   │   ├── Auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── Assignments/
│   │   │   ├── AssignmentCard.tsx
│   │   │   ├── AssignmentList.tsx
│   │   │   └── AssignmentTimeline.tsx
│   │   ├── Jobs/
│   │   │   ├── JobCard.tsx
│   │   │   └── JobList.tsx
│   │   └── Approvals/
│   │       └── PendingApprovalCard.tsx
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Assignments.tsx
│   │   ├── Jobs.tsx
│   │   ├── Settings.tsx
│   │   └── Integrations.tsx
│   ├── api/
│   │   ├── client.ts  # Axios instance
│   │   ├── auth.ts
│   │   ├── assignments.ts
│   │   └── jobs.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useAssignments.ts
│   │   └── useJobs.ts
│   ├── store/
│   │   └── authStore.ts
│   └── App.tsx
```

### 2.3 Key Pages to Build

**Dashboard Page:**
- Timeline view of upcoming deadlines
- Recent emails
- Pending approvals
- Quick stats (assignments due this week, job applications pending)

**Assignments Page:**
- Filterable list (by course, status, source)
- Calendar view
- Grade tracking

**Jobs Page:**
- Saved jobs with match scores
- Application tracker
- Cover letter generation

**Settings/Integrations Page:**
- Connect Canvas account
- Connect Gmail
- Connect Gradescope
- Trigger manual sync

---

## Phase 3: Web Scraping Services (Week 2-3)

### 3.1 Canvas Integration (API - Easiest!)

**Canvas provides official REST API:**
- Base URL: `https://<institution>.instructure.com/api/v1/`
- Requires API token (user generates in Canvas settings)

**Endpoints to use:**
```python
# In app/services/canvas_scraper.py

GET /api/v1/courses
GET /api/v1/courses/:id/assignments
GET /api/v1/courses/:id/assignment_groups
GET /api/v1/courses/:id/enrollments
GET /api/v1/users/self/courses
```

**Implementation:**
```python
class CanvasScraper:
    def __init__(self, api_token: str, base_url: str):
        self.token = api_token
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_token}"}

    async def fetch_courses(self) -> List[dict]:
        """Fetch all active courses for user."""
        url = f"{self.base_url}/api/v1/courses"
        params = {"enrollment_state": "active", "per_page": 100}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            return response.json()

    async def fetch_assignments(self, course_id: int) -> List[dict]:
        """Fetch all assignments for a course."""
        url = f"{self.base_url}/api/v1/courses/{course_id}/assignments"
        # ... implementation
```

### 3.2 Gmail Integration (API - Medium)

**Use Google Gmail API:**

**Setup:**
1. Create project in Google Cloud Console
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. User grants permission

**Implementation:**
```python
# In app/services/gmail_scraper.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailScraper:
    def __init__(self, credentials: dict):
        self.creds = Credentials.from_authorized_user_info(credentials)
        self.service = build('gmail', 'v1', credentials=self.creds)

    async def fetch_academic_emails(self, max_results: int = 100):
        """Fetch emails from .edu domains or with academic keywords."""
        query = 'from:*.edu OR subject:(assignment OR grade OR due OR homework)'
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        # ... process results
```

### 3.3 Gradescope Scraping (Complex - No API)

**Use Playwright (already in requirements.txt):**

```python
# In app/services/gradescope_scraper.py

from playwright.async_api import async_playwright

class GradescopeScraper:
    async def scrape_assignments(self, email: str, password: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Login
            await page.goto("https://www.gradescope.com/login")
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="password"]', password)
            await page.click('button[type="submit"]')

            # Wait for redirect
            await page.wait_for_url("**/account")

            # Navigate to courses
            await page.goto("https://www.gradescope.com/courses")

            # Extract course data
            courses = await page.query_selector_all('.courseList--term')
            # ... parse HTML
```

**⚠️ Important:** Add rate limiting, error handling, and respect robots.txt

### 3.4 LinkedIn Job Extraction (Manual Entry MVP)

**Start with manual URL entry to avoid ToS violations:**

```python
# In app/services/linkedin_scraper.py

async def extract_job_from_url(url: str) -> dict:
    """
    User provides LinkedIn job URL.
    Extract job details from that specific page.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract structured data
        job_data = {
            "title": soup.find("h1", class_="job-title").text,
            "company": soup.find("a", class_="company-name").text,
            # ... etc
        }
        return job_data
```

---

## Phase 4: Approval Workflows (Week 3)

### 4.1 Backend API Additions

**New endpoints:**

```python
# In app/api/v1/approvals.py

@router.get("/pending")
async def get_pending_approvals(current_user: User = Depends(get_current_user)):
    """Get all items pending user approval."""
    # Return assignments, courses, emails, jobs where approved=False

@router.post("/assignments/{id}/approve")
async def approve_assignment(id: int, approved: bool):
    """Approve or reject scraped assignment."""

@router.post("/assignments/bulk-approve")
async def bulk_approve_assignments(ids: List[int]):
    """Approve multiple assignments at once."""
```

### 4.2 Frontend Approval UI

**Pending Approvals Dashboard:**
- Show count badges (e.g., "5 new assignments to review")
- Preview card with source info
- Approve/Reject/Edit buttons
- Bulk actions

---

## MVP Scope Recommendation

**Build in this order:**

### Week 1: Foundation
- [ ] Extend database schema (add new models)
- [ ] Create Alembic migration
- [ ] Set up React frontend boilerplate
- [ ] Build auth pages (login/register)
- [ ] Create dashboard layout

### Week 2: First Integration
- [ ] Implement Canvas API integration
- [ ] Create "Connect Canvas" flow in settings
- [ ] Scrape courses and assignments from Canvas
- [ ] Display in frontend
- [ ] Add approval workflow for Canvas data

### Week 3: Additional Integrations
- [ ] Gmail integration (OAuth flow)
- [ ] Gradescope scraper (Playwright)
- [ ] Display aggregated timeline

### Week 4: Job Features
- [ ] Manual LinkedIn job URL entry
- [ ] Job data extraction
- [ ] Requirement parsing (use existing AI features)
- [ ] Job-to-resume matching (already have this!)

---

## Security Checklist

- [ ] Encrypt credentials at rest (use Fernet from cryptography library)
- [ ] Store encryption key in Railway environment variables
- [ ] Never log passwords or tokens
- [ ] Validate all user inputs
- [ ] Add rate limiting on scraping endpoints
- [ ] Implement CORS properly
- [ ] Use HTTPS only
- [ ] Add CSRF protection on state-changing endpoints

---

## Deployment Strategy

**Backend (already deployed on Railway):**
- Keep current deployment
- Add new environment variables as needed
- Redeploy automatically on git push

**Frontend:**
- Deploy to Railway static site OR Vercel
- Set API_BASE_URL environment variable
- Enable CORS on backend for frontend domain

---

## Testing Strategy

**Backend:**
- Unit tests for scrapers (mock external APIs)
- Integration tests for approval workflows
- Test credential encryption/decryption

**Frontend:**
- Test API integration with MSW (Mock Service Worker)
- Component tests with React Testing Library

---

## Cost Estimates

**Railway:**
- Hobby plan: $5/month (includes PostgreSQL)
- Should be sufficient for MVP

**External APIs:**
- Canvas API: Free (user provides token)
- Gmail API: Free (within quota)
- OpenAI API: ~$10-20/month for cover letter generation

**Total: ~$15-25/month**

---

## Next Immediate Steps

1. **Review this plan** - Does it align with your vision?
2. **Decide on database changes** - Should I create the migration?
3. **Set up frontend** - Should I initialize the React project?
4. **Pick first integration** - Canvas recommended (easiest, has API)

**Ready to start? Let me know which phase you want to tackle first!**
