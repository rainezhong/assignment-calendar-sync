# Student Hub - Intern Onboarding Guide

**Welcome!** This document will help you understand the Student Hub project and prepare you to polish and improve it.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Getting Started](#getting-started)
4. [Learning Topics with Code Examples](#learning-topics-with-code-examples)
5. [Codebase Tour](#codebase-tour)
6. [Common Tasks](#common-tasks)
7. [Areas for Polishing](#areas-for-polishing)
8. [Resources](#resources)

---

## Project Overview

### What is Student Hub?

Student Hub is a unified platform that helps students manage their academic life by:
- **Syncing assignments** from Canvas LMS
- **Extracting deadlines** from Gmail emails
- **Tracking grades** from Gradescope
- **Finding matching jobs** from LinkedIn based on coursework
- **AI-powered insights** about assignment complexity and workload

### Technology Stack

**Backend (Python):**
- FastAPI - Modern async web framework
- SQLAlchemy 2.0 - Async ORM for database
- PostgreSQL - Relational database
- Playwright - Browser automation for web scraping
- Alembic - Database migrations
- Pydantic - Data validation

**Frontend (React + TypeScript):**
- React 18 - UI library
- TypeScript - Type-safe JavaScript
- TanStack Query - Server state management
- Zustand - Client state management
- Tailwind CSS - Utility-first styling
- Vite - Build tool

**Deployment:**
- Railway - Backend hosting
- Vercel - Frontend hosting

---

## Architecture Overview

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌──────────────────────────────────────┐
│         FastAPI Backend              │
│  ┌────────────────────────────────┐ │
│  │    Authentication (JWT)        │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │      API Endpoints             │ │
│  │  /auth  /assignments  /jobs    │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │       Services Layer           │ │
│  │  - LinkedIn scraping           │ │
│  │  - Job matching                │ │
│  │  - Canvas OAuth                │ │
│  │  - Gmail OAuth                 │ │
│  │  - Gradescope scraping         │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │   SQLAlchemy Models (ORM)      │ │
│  └────────────────────────────────┘ │
└──────────────┬───────────────────────┘
               │
               ▼
        ┌─────────────┐
        │ PostgreSQL  │
        │  Database   │
        └─────────────┘
```

### Key Design Patterns

1. **Repository Pattern**: Database access through SQLAlchemy ORM
2. **Service Layer**: Business logic separated from API endpoints
3. **Dependency Injection**: FastAPI's `Depends()` for database sessions, auth
4. **OAuth 2.0**: Secure third-party integrations (Canvas, Gmail)
5. **Web Scraping**: Playwright for sites without APIs (Gradescope, LinkedIn)

---

## Getting Started

### Prerequisites

Install these tools:
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone <repo-url>
cd assignment-calendar-sync
```

2. **Backend setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/studenthub
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

3. **Frontend setup**
```bash
cd frontend
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start frontend
npm run dev
```

4. **Access the app**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Learning Topics with Code Examples

### 1. Async/Await in Python (FastAPI)

**Why it matters**: The entire backend is asynchronous for better performance.

**Example from** `backend/app/api/v1/assignments.py:26-42`:
```python
@router.get("/", response_model=List[AssignmentResponse])
async def get_assignments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all assignments for current user."""
    result = await db.execute(
        select(Assignment)
        .where(Assignment.user_id == current_user.id)
        .order_by(Assignment.due_date)
    )
    assignments = result.scalars().all()
    return assignments
```

**Key concepts**:
- `async def` - Declares async function
- `await` - Waits for async operation to complete
- `AsyncSession` - Async database session
- `Depends()` - Dependency injection

**Learning resources**:
- FastAPI async tutorial: https://fastapi.tiangolo.com/async/
- Python asyncio docs: https://docs.python.org/3/library/asyncio.html

---

### 2. SQLAlchemy 2.0 ORM

**Why it matters**: All database operations use SQLAlchemy's async ORM.

**Example from** `backend/app/models/assignment.py:9-36`:
```python
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    user = relationship("User", back_populates="assignments")
    course = relationship("Course", back_populates="assignments")
```

**Querying example from** `backend/app/api/v1/jobs.py:189-207`:
```python
# Build query
query = select(JobMatch).where(JobMatch.user_id == current_user.id)

# Apply filters
if job_type:
    query = query.join(JobListing).where(JobListing.job_type == job_type)

# Apply sorting
if sort_by == "match_score":
    query = query.order_by(desc(JobMatch.match_score))

# Execute query
result = await db.execute(query)
job_matches = result.scalars().all()
```

**Key concepts**:
- `Column()` - Define table columns
- `ForeignKey()` - Define relationships between tables
- `relationship()` - ORM-level relationships
- `select()` - Build SQL queries
- `join()` - Join tables
- `where()` - Filter conditions
- `order_by()` - Sorting

**Learning resources**:
- SQLAlchemy 2.0 tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- Async ORM: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

### 3. Pydantic Models for Validation

**Why it matters**: Type-safe request/response validation with automatic error messages.

**Example from** `backend/app/api/v1/jobs.py:23-33`:
```python
class ScrapeJobsRequest(BaseModel):
    search_url: str
    max_jobs: int = 25

class ScrapeJobsResponse(BaseModel):
    status: str
    message: str
    jobs_found: int
    jobs_new: int
```

**Usage in endpoint** `backend/app/api/v1/jobs.py:70-75`:
```python
@router.post("/scrape", response_model=ScrapeJobsResponse)
async def scrape_jobs(
    request: ScrapeJobsRequest,  # Pydantic validates incoming JSON
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # request.search_url is guaranteed to be a string
    # request.max_jobs is guaranteed to be an int (default 25)
```

**Key concepts**:
- `BaseModel` - Base class for Pydantic models
- Automatic validation - Invalid data returns 422 error
- `response_model` - Validates outgoing responses
- Default values - `max_jobs: int = 25`

**Learning resources**:
- Pydantic docs: https://docs.pydantic.dev/latest/
- FastAPI with Pydantic: https://fastapi.tiangolo.com/tutorial/body/

---

### 4. JWT Authentication

**Why it matters**: Secure user authentication without sessions.

**Token creation** `backend/app/core/security.py:15-26`:
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
```

**Token verification** `backend/app/core/deps.py:12-33`:
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        # Get user from database
        result = await db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
```

**Protecting endpoints** `backend/app/api/v1/assignments.py:26-29`:
```python
@router.get("/")
async def get_assignments(
    current_user: User = Depends(get_current_user),  # ← Requires valid JWT
    db: AsyncSession = Depends(get_db),
):
    # Only runs if user is authenticated
    # current_user contains the authenticated User object
```

**Key concepts**:
- JWT - JSON Web Tokens for stateless auth
- `Bearer token` - Sent in Authorization header
- Token expiration - Tokens expire after set time
- Dependency injection - `Depends(get_current_user)` protects endpoints

**Learning resources**:
- JWT.io: https://jwt.io/introduction
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

---

### 5. React Query (TanStack Query)

**Why it matters**: Handles server state, caching, and synchronization automatically.

**Example from** `frontend/src/pages/Jobs.tsx:13-16`:
```typescript
// Get all jobs
const { data: jobs, isLoading } = useQuery({
  queryKey: ['jobs'],
  queryFn: () => jobsApi.getJobs({ sort_by: 'match_score' }),
});
```

**Mutation example** `frontend/src/pages/Jobs.tsx:19-30`:
```typescript
// Scrape mutation
const scrapeMutation = useMutation({
  mutationFn: (data: ScrapeJobsRequest) => jobsApi.scrapeJobs(data),
  onSuccess: (data) => {
    queryClient.invalidateQueries({ queryKey: ['jobs'] });  // ← Refetch jobs
    setSearchUrl('');
    setError('');
    alert(`Success! Found ${data.jobs_found} jobs (${data.jobs_new} new)`);
  },
  onError: (err: any) => {
    setError(err.response?.data?.detail || 'Failed to scrape jobs');
  },
});
```

**Key concepts**:
- `useQuery` - Fetch and cache data
- `useMutation` - Create/update/delete operations
- `queryKey` - Unique identifier for cached data
- `invalidateQueries` - Refetch data after mutation
- Automatic loading/error states

**Learning resources**:
- TanStack Query docs: https://tanstack.com/query/latest
- React Query tutorial: https://ui.dev/react-query-tutorial

---

### 6. Playwright Web Scraping

**Why it matters**: Automates browsers to scrape sites without APIs (Gradescope, LinkedIn).

**Example from** `backend/app/services/linkedin_service.py:88-130`:
```python
async def scrape_job_search(self, search_url: str, max_jobs: int = 25) -> List[Dict]:
    """Scrape job listings from LinkedIn search URL"""

    # Navigate to search URL
    await self.page.goto(search_url, wait_until='networkidle', timeout=30000)
    await asyncio.sleep(2)  # Let page fully load

    # Find all job cards
    job_cards = await self.page.query_selector_all('.job-search-card, .base-card')

    jobs = []
    for card in job_cards[:max_jobs]:
        try:
            # Extract job title
            title_elem = await card.query_selector('h3, .job-card-list__title')
            title = await title_elem.inner_text() if title_elem else 'Unknown'

            # Extract company
            company_elem = await card.query_selector('.job-card-container__company-name')
            company = await company_elem.inner_text() if company_elem else 'Unknown'

            # Extract location
            location_elem = await card.query_selector('.job-card-container__metadata-item')
            location = await location_elem.inner_text() if location_elem else 'Unknown'

            # Get job URL
            link_elem = await card.query_selector('a')
            job_url = await link_elem.get_attribute('href') if link_elem else None

            jobs.append({
                'title': title.strip(),
                'company': company.strip(),
                'location': location.strip(),
                'job_url': job_url,
            })
        except Exception as e:
            logging.warning(f"Failed to parse job card: {e}")
            continue

    return jobs
```

**Browser lifecycle** `backend/app/services/linkedin_service.py:43-85`:
```python
async def __aenter__(self):
    """Async context manager entry"""
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Cleanup browser on exit"""
    await self.cleanup()

async def initialize(self):
    """Initialize Playwright browser"""
    self.playwright = await async_playwright().start()
    self.browser = await self.playwright.chromium.launch(
        headless=True,  # Run without GUI
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    self.context = await self.browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
        viewport={'width': 1920, 'height': 1080}
    )
    self.page = await self.context.new_page()

async def cleanup(self):
    """Close browser"""
    if self.page:
        await self.page.close()
    if self.context:
        await self.context.close()
    if self.browser:
        await self.browser.close()
    if self.playwright:
        await self.playwright.stop()
```

**Usage pattern**:
```python
async with LinkedInService() as linkedin:
    await linkedin.initialize()
    jobs = await linkedin.scrape_job_search(url, max_jobs=25)
# Browser automatically cleaned up after 'with' block
```

**Key concepts**:
- Headless browser - Runs without GUI
- Selectors - CSS selectors to find elements
- `query_selector()` - Find single element
- `query_selector_all()` - Find all matching elements
- `inner_text()` - Extract text content
- Error handling - Defensive coding for missing elements
- Context manager - Automatic cleanup

**Learning resources**:
- Playwright Python: https://playwright.dev/python/docs/intro
- Web scraping guide: https://scrapingant.com/blog/web-scraping-with-playwright

---

### 7. OAuth 2.0 Flow

**Why it matters**: Secure integration with Canvas and Gmail without storing passwords.

**OAuth initiation** `backend/app/api/v1/canvas.py:28-55`:
```python
@router.post("/connect", response_model=CanvasConnectionResponse)
async def connect_canvas(
    request: CanvasConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect user's Canvas account"""

    # Encrypt the API token
    encrypted_token = encryption_service.encrypt(request.api_token)

    # Test the connection
    async with CanvasService(request.base_url, request.api_token) as canvas:
        try:
            # Verify token works
            canvas_user = await canvas.get_current_user()

            # Store encrypted credentials
            integration = CanvasIntegration(
                user_id=current_user.id,
                institution_url=request.base_url,
                access_token=encrypted_token,  # ← Encrypted!
                canvas_user_id=canvas_user['id'],
            )
            db.add(integration)
            await db.commit()

            return CanvasConnectionResponse(
                status="success",
                message="Canvas connected successfully",
                canvas_user=canvas_user,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
```

**Encryption service** `backend/app/services/encryption_service.py:8-25`:
```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self):
        # Load encryption key from environment
        self.key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data"""
        if not plaintext:
            return ""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted:
            return ""
        decrypted = self.cipher.decrypt(encrypted.encode())
        return decrypted.decode()
```

**Key concepts**:
- OAuth tokens - Access third-party APIs on behalf of user
- Encryption - Never store tokens in plaintext
- Fernet - Symmetric encryption for tokens
- Token validation - Test token before storing

**Learning resources**:
- OAuth 2.0 explained: https://oauth.net/2/
- Cryptography library: https://cryptography.io/en/latest/

---

### 8. TypeScript Types & Interfaces

**Why it matters**: Type safety prevents bugs and improves code quality.

**Example from** `frontend/src/types/index.ts:239-255`:
```typescript
export interface JobListingResponse {
  id: number;
  title: string;
  company: string;
  location: string;
  remote_type: string;
  job_type: string;
  description?: string;  // ← Optional field
  salary_min?: number;
  salary_max?: number;
  application_url: string;
  source: string;
  posted_date?: string;
  skills: string[];
  match_score?: number;
  matched_skills?: string[];
}
```

**Usage in component** `frontend/src/pages/Jobs.tsx:145-253`:
```typescript
{jobs.map((job: JobListingResponse) => (  // ← Type annotation
  <div key={job.id} className="card">
    {/* TypeScript knows all available properties */}
    <h3>{job.title}</h3>
    <span>{job.company}</span>

    {/* TypeScript enforces optional checking */}
    {job.match_score !== undefined && (
      <span>{job.match_score}% Match</span>
    )}

    {/* Array methods are type-safe */}
    {job.matched_skills?.slice(0, 5).map((skill, idx) => (
      <span key={idx}>{skill}</span>
    ))}
  </div>
))}
```

**API client typing** `frontend/src/api/jobs.ts:9-16`:
```typescript
export const jobsApi = {
  /**
   * Scrape jobs from LinkedIn search URL
   */
  scrapeJobs: async (data: ScrapeJobsRequest): Promise<ScrapeJobsResponse> => {
    const response = await apiClient.post<ScrapeJobsResponse>('/jobs/scrape', data);
    return response.data;
  },
}
```

**Key concepts**:
- `interface` - Define object shapes
- Optional properties - `field?: type`
- Type annotations - `: Type`
- Generics - `<T>`
- Type inference - TypeScript figures out types automatically

**Learning resources**:
- TypeScript handbook: https://www.typescriptlang.org/docs/handbook/intro.html
- React TypeScript cheatsheet: https://react-typescript-cheatsheet.netlify.app/

---

### 9. Tailwind CSS Utility Classes

**Why it matters**: Rapid UI development without writing custom CSS.

**Example from** `frontend/src/pages/Jobs.tsx:146-177`:
```tsx
<div key={job.id} className="card hover:shadow-md transition-shadow">
  <div className="flex items-start justify-between gap-4">
    <div className="flex-1 min-w-0">
      {/* Match Score Badge */}
      {job.match_score !== undefined && (
        <div className="flex items-center gap-2 mb-2">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getMatchScoreColor(job.match_score)}`}>
            <TrendingUp className="w-3 h-3 mr-1" />
            {job.match_score}% Match
          </span>
        </div>
      )}

      {/* Job Title */}
      <h3 className="text-lg font-semibold text-gray-900 mb-1">
        {job.title}
      </h3>

      {/* Company and Location */}
      <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
        <div className="flex items-center gap-1.5">
          <Building2 className="w-4 h-4" />
          <span>{job.company}</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

**Common utility patterns**:
```
Layout:
- flex, grid
- items-center, justify-between
- gap-4, space-y-3

Spacing:
- p-4 (padding), m-4 (margin)
- px-3 (horizontal padding)
- mb-2 (margin bottom)

Sizing:
- w-4 (width), h-4 (height)
- max-w-6xl, min-w-0

Typography:
- text-lg, text-sm
- font-semibold, font-medium
- text-gray-900, text-blue-700

Colors:
- bg-green-100, bg-blue-50
- text-green-800, text-gray-600
- border-gray-300

Effects:
- rounded-md, rounded-full
- shadow-md, hover:shadow-lg
- transition-shadow
```

**Dynamic classes** `frontend/src/pages/Jobs.tsx:57-62`:
```typescript
const getMatchScoreColor = (score?: number) => {
  if (!score) return 'bg-gray-100 text-gray-800';
  if (score >= 80) return 'bg-green-100 text-green-800';
  if (score >= 60) return 'bg-yellow-100 text-yellow-800';
  return 'bg-gray-100 text-gray-800';
};
```

**Learning resources**:
- Tailwind docs: https://tailwindcss.com/docs
- Tailwind cheatsheet: https://nerdcave.com/tailwind-cheat-sheet

---

### 10. Database Migrations with Alembic

**Why it matters**: Version control for database schema changes.

**Example migration** `backend/alembic/versions/xxx_add_job_listings.py`:
```python
"""add job listings

Revision ID: abc123
Revises: previous_revision
Create Date: 2025-11-23
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'previous_revision'

def upgrade():
    """Apply changes"""
    op.create_table(
        'job_listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('skills', sa.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    """Revert changes"""
    op.drop_table('job_listings')
```

**Common commands**:
```bash
# Create new migration
alembic revision --autogenerate -m "add user table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

**Learning resources**:
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html

---

## Codebase Tour

### Backend Structure

```
backend/
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py     # Register all routers
│   │       ├── auth.py         # Login, register, refresh token
│   │       ├── assignments.py  # CRUD assignments
│   │       ├── canvas.py       # Canvas OAuth & sync
│   │       ├── gmail.py        # Gmail OAuth & sync
│   │       ├── gradescope.py   # Gradescope scraping
│   │       └── jobs.py         # LinkedIn jobs scraping
│   ├── core/
│   │   ├── config.py           # Settings from environment
│   │   ├── deps.py             # Dependency injection (auth, db)
│   │   └── security.py         # JWT, password hashing
│   ├── db/
│   │   ├── base.py             # Import all models
│   │   └── session.py          # Database session management
│   ├── models/                 # SQLAlchemy models (database tables)
│   │   ├── user.py
│   │   ├── assignment.py
│   │   ├── course.py
│   │   ├── job_listing.py
│   │   └── job_match.py
│   ├── services/               # Business logic
│   │   ├── canvas_service.py
│   │   ├── gmail_service.py
│   │   ├── gradescope_service.py
│   │   ├── linkedin_service.py
│   │   ├── job_matching_service.py
│   │   └── encryption_service.py
│   └── main.py                 # FastAPI app entry point
├── requirements.txt            # Python dependencies
└── alembic.ini                 # Alembic configuration
```

### Frontend Structure

```
frontend/
├── src/
│   ├── api/                    # API clients
│   │   ├── client.ts           # Axios instance with auth
│   │   ├── auth.ts             # Auth endpoints
│   │   ├── assignments.ts      # Assignment endpoints
│   │   ├── canvas.ts           # Canvas endpoints
│   │   ├── gmail.ts            # Gmail endpoints
│   │   ├── gradescope.ts       # Gradescope endpoints
│   │   └── jobs.ts             # Jobs endpoints
│   ├── components/             # Reusable components
│   │   ├── Layout.tsx          # App layout with navbar
│   │   └── ProtectedRoute.tsx  # Auth guard for routes
│   ├── hooks/                  # Custom React hooks
│   │   └── useAuth.ts          # Auth state management
│   ├── pages/                  # Page components (routes)
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Assignments.tsx
│   │   ├── Settings.tsx        # Integrations management
│   │   └── Jobs.tsx            # LinkedIn jobs
│   ├── store/                  # Zustand state management
│   │   └── authStore.ts        # Global auth state
│   ├── types/                  # TypeScript types
│   │   └── index.ts            # All interface definitions
│   ├── App.tsx                 # Root component with routes
│   ├── main.tsx                # React entry point
│   └── index.css               # Global styles + Tailwind
├── package.json                # Node dependencies
└── vite.config.ts              # Vite build configuration
```

---

## Common Tasks

### 1. Adding a New API Endpoint

**Step 1**: Create Pydantic schemas in endpoint file
```python
# backend/app/api/v1/my_feature.py
from pydantic import BaseModel

class CreateItemRequest(BaseModel):
    name: str
    description: str

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 2**: Create endpoint
```python
@router.post("/items", response_model=ItemResponse)
async def create_item(
    request: CreateItemRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_item = Item(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item
```

**Step 3**: Register router
```python
# backend/app/api/v1/__init__.py
from app.api.v1 import my_feature

api_router.include_router(my_feature.router, prefix="/my-feature", tags=["my-feature"])
```

**Step 4**: Test in API docs at http://localhost:8000/docs

---

### 2. Adding a New Frontend Page

**Step 1**: Create page component
```tsx
// frontend/src/pages/MyPage.tsx
import { useQuery } from '@tanstack/react-query';

export default function MyPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: () => fetch('/api/v1/items').then(r => r.json()),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">My Page</h1>
      {/* Your content */}
    </div>
  );
}
```

**Step 2**: Add route
```tsx
// frontend/src/App.tsx
import MyPage from './pages/MyPage';

function App() {
  return (
    <Routes>
      {/* Existing routes */}
      <Route path="/my-page" element={
        <ProtectedRoute>
          <MyPage />
        </ProtectedRoute>
      } />
    </Routes>
  );
}
```

**Step 3**: Add navigation link
```tsx
// frontend/src/components/Layout.tsx
<nav>
  <Link to="/my-page">My Page</Link>
</nav>
```

---

### 3. Creating a Database Migration

**Step 1**: Modify model
```python
# backend/app/models/assignment.py
class Assignment(Base):
    __tablename__ = "assignments"

    # Add new column
    priority = Column(String, default="medium")
```

**Step 2**: Generate migration
```bash
cd backend
alembic revision --autogenerate -m "add priority to assignments"
```

**Step 3**: Review generated migration
```python
# backend/alembic/versions/xxx_add_priority.py
def upgrade():
    op.add_column('assignments', sa.Column('priority', sa.String(), nullable=True))

def downgrade():
    op.drop_column('assignments', 'priority')
```

**Step 4**: Apply migration
```bash
alembic upgrade head
```

---

### 4. Debugging a Backend Issue

**Step 1**: Check logs
```bash
# Backend prints to console
uvicorn app.main:app --reload
```

**Step 2**: Add logging
```python
import logging

logging.info(f"Processing user {user_id}")
logging.warning(f"Unexpected value: {value}")
logging.error(f"Failed to process: {e}")
```

**Step 3**: Use API docs for manual testing
- Go to http://localhost:8000/docs
- Click endpoint → "Try it out"
- Fill in parameters
- Click "Execute"

**Step 4**: Check database
```bash
# Connect to PostgreSQL
psql -U username -d studenthub

# View tables
\dt

# Query data
SELECT * FROM users;
SELECT * FROM assignments WHERE user_id = 1;
```

---

### 5. Debugging a Frontend Issue

**Step 1**: Open browser DevTools (F12)
- Console: JavaScript errors
- Network: API requests/responses
- React DevTools: Component state

**Step 2**: Check React Query DevTools
```tsx
// frontend/src/App.tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

**Step 3**: Add console.logs
```tsx
console.log('User data:', user);
console.log('API response:', data);
```

**Step 4**: Check API calls
```tsx
// Check request
const response = await apiClient.get('/assignments');
console.log('Status:', response.status);
console.log('Data:', response.data);
```

---

## Areas for Polishing

### High Priority

#### 1. Error Handling & User Feedback
**Current issue**: Generic error messages, inconsistent error handling

**Example locations**:
- `frontend/src/pages/Jobs.tsx:27-29` - Basic error display
- `backend/app/api/v1/jobs.py:171-175` - Generic 500 errors

**Improvements needed**:
- User-friendly error messages
- Toast notifications instead of alerts
- Error boundaries in React
- Proper HTTP status codes
- Error logging/monitoring

**Learning topics**: Error handling patterns, React Error Boundaries, Toast libraries (react-hot-toast)

---

#### 2. Loading States & Skeletons
**Current issue**: Basic loading spinners, no skeleton screens

**Example locations**:
- `frontend/src/pages/Jobs.tsx:129-135` - Simple loading spinner
- All pages have basic loading states

**Improvements needed**:
- Skeleton screens for better UX
- Progressive loading
- Optimistic updates
- Loading state consistency

**Learning topics**: React Suspense, Skeleton patterns, Optimistic UI updates

---

#### 3. Form Validation
**Current issue**: Minimal client-side validation

**Example locations**:
- `frontend/src/pages/Jobs.tsx:44-52` - Basic URL validation
- Login/Register forms need better validation

**Improvements needed**:
- React Hook Form integration
- Zod schema validation
- Real-time validation feedback
- Better error messages

**Learning topics**: React Hook Form, Zod, Form validation patterns

**Example implementation**:
```tsx
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  search_url: z.string().url().includes('linkedin.com'),
  max_jobs: z.number().min(1).max(100),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

---

#### 4. Accessibility (a11y)
**Current issue**: No focus management, missing ARIA labels

**Improvements needed**:
- Keyboard navigation
- Screen reader support
- Focus management
- ARIA labels
- Color contrast compliance

**Learning topics**: WCAG guidelines, ARIA attributes, Semantic HTML

**Quick wins**:
```tsx
// Add ARIA labels
<button aria-label="Scrape jobs from LinkedIn">
  <Search /> Scrape Jobs
</button>

// Keyboard navigation
<div role="list" aria-label="Job listings">
  {jobs.map(job => (
    <article key={job.id} role="listitem" tabIndex={0}>
      {/* Job content */}
    </article>
  ))}
</div>
```

---

#### 5. Testing
**Current issue**: No tests at all!

**Improvements needed**:
- Backend: pytest for API tests
- Frontend: Vitest + React Testing Library
- E2E tests: Playwright

**Learning topics**: pytest, Vitest, React Testing Library, E2E testing

**Example backend test**:
```python
# backend/tests/test_assignments.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_assignments(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/assignments/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Example frontend test**:
```tsx
// frontend/src/pages/__tests__/Jobs.test.tsx
import { render, screen } from '@testing-library/react';
import Jobs from '../Jobs';

test('renders jobs page', () => {
  render(<Jobs />);
  expect(screen.getByText('Job Matches')).toBeInTheDocument();
});
```

---

### Medium Priority

#### 6. Performance Optimization
**Issues**:
- Large bundle size
- No code splitting
- N+1 queries in some endpoints

**Improvements**:
- Lazy loading routes
- Database query optimization
- Caching strategies
- Image optimization

**Example optimization** `frontend/src/App.tsx`:
```tsx
import { lazy, Suspense } from 'react';

const Jobs = lazy(() => import('./pages/Jobs'));

<Route path="/jobs" element={
  <Suspense fallback={<LoadingSpinner />}>
    <ProtectedRoute><Jobs /></ProtectedRoute>
  </Suspense>
} />
```

---

#### 7. Mobile Responsiveness
**Issue**: Desktop-first design, poor mobile UX

**Improvements**:
- Mobile-first Tailwind breakpoints
- Touch-friendly targets
- Responsive navigation
- Mobile testing

**Example**:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Stacks on mobile, 2 columns on tablet, 3 on desktop */}
</div>
```

---

#### 8. Code Organization
**Issues**:
- Large component files
- Duplicated logic
- No custom hooks

**Improvements**:
- Extract reusable components
- Create custom hooks
- Utility functions
- Consistent file structure

**Example custom hook**:
```tsx
// frontend/src/hooks/useJobs.ts
export function useJobs(filters?: JobFilters) {
  return useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => jobsApi.getJobs(filters),
  });
}

// Usage
const { data: jobs, isLoading } = useJobs({ sort_by: 'match_score' });
```

---

#### 9. Security Hardening
**Issues to review**:
- Rate limiting
- CORS configuration
- SQL injection prevention (SQLAlchemy helps)
- XSS prevention (React helps)
- CSRF tokens

**Improvements**:
```python
# backend/app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(...):
    ...
```

---

#### 10. Documentation
**Missing**:
- API documentation beyond OpenAPI
- Component documentation
- Setup troubleshooting
- Architecture decisions

**Improvements**:
- Storybook for components
- API usage examples
- Troubleshooting guide
- Architecture decision records (ADRs)

---

### Low Priority (Nice to Have)

- Dark mode
- Email notifications
- Calendar export (iCal)
- Assignment reminders
- Advanced filters/search
- Dashboard customization
- Export data (CSV, PDF)
- Analytics/insights page
- Batch operations

---

## Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/docs/
- **TanStack Query**: https://tanstack.com/query/latest
- **Tailwind CSS**: https://tailwindcss.com/docs
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Playwright**: https://playwright.dev/python/

### Learning Paths

**Backend Focus**:
1. FastAPI tutorial (official docs)
2. SQLAlchemy async tutorial
3. Pydantic validation
4. JWT authentication
5. Web scraping with Playwright

**Frontend Focus**:
1. React hooks deep dive
2. TypeScript fundamentals
3. TanStack Query guide
4. Tailwind CSS mastery
5. Form handling with React Hook Form

**Full Stack**:
1. REST API design
2. Database design & normalization
3. Authentication flows
4. State management patterns
5. Testing strategies

### Communities
- **Discord**: FastAPI, React, TypeScript communities
- **Reddit**: r/FastAPI, r/reactjs, r/typescript
- **Stack Overflow**: Tag questions appropriately

---

## Next Steps

1. **Week 1**: Set up local environment, run the app, explore codebase
2. **Week 2**: Pick a high-priority polishing task (start small!)
3. **Week 3**: Add tests for your changes
4. **Week 4**: Tackle a medium-priority task
5. **Ongoing**: Document your changes, ask questions, iterate

---

## Questions?

When you have questions:
1. Check this document first
2. Search the codebase for similar patterns
3. Check official documentation
4. Ask your mentor/team

**Good luck! You've got this! 🚀**
