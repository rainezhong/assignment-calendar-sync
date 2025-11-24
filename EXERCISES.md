# Student Hub: Learning Exercises

Welcome! This guide will help you deeply understand the Student Hub architecture while making real improvements. Work through these exercises in order—each builds on knowledge from previous ones.

**Your Background:**
- ✅ Python basics, Git
- 🆕 Async/await, SQLAlchemy, FastAPI, React, TypeScript, REST APIs

**Your Goal:** Understand this full-stack app AND get it production-ready

---

## 📋 Pre-Flight Checklist

Complete these steps before starting exercises:

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Check Python version (need 3.11+)
python3 --version

# 3. Install dependencies (if not already done)
pip install -r requirements.txt

# 4. Verify environment variables
cat .env  # Should have DATABASE_URL, SECRET_KEY, etc.

# 5. Check database connection
psql $DATABASE_URL -c "SELECT 1;"

# 6. Run migrations
alembic upgrade head

# 7. Start backend server
uvicorn app.main:app --reload
```

**✅ Verify:** Open http://localhost:8000/docs - Should see FastAPI Swagger UI

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Check Node version (need 18+)
node --version

# 3. Install dependencies
npm install

# 4. Verify environment variables
cat .env  # Should have VITE_API_URL

# 5. Start frontend
npm run dev
```

**✅ Verify:** Open http://localhost:5173 - Should see login page

### Quick Health Check

```bash
# Backend health
curl http://localhost:8000/api/v1/auth/me

# Expected: 401 Unauthorized (need token)

# Frontend to backend connection
# Open browser console on http://localhost:5173/login
# Should see no CORS errors
```

---

## Module 1: Understanding the Architecture (Estimated: 2-3 hours)

### Exercise 1.1: Trace a Complete Request ⭐️ START HERE

**Objective:** Follow a login request from button click to database and back

**Why This Matters:** Understanding the full request flow is fundamental to working with this codebase. You'll see how all the pieces (React → API client → FastAPI → Database → Response) connect together.

**Starting Point:** `/Users/raine/assignment-calendar-sync/frontend/src/pages/Login.tsx:15`

#### Tasks:

- [ ] **Step 1:** Open `Login.tsx` and find the `handleSubmit` function (line 15)
  - What happens when user clicks "Login"?
  - Which Zustand store method is called?

- [ ] **Step 2:** Open `frontend/src/store/authStore.ts` line 25
  - Find the `login` async function
  - What API method does it call?
  - Where does it store the token after success?

- [ ] **Step 3:** Open `frontend/src/api/auth.ts` line 5
  - What HTTP method is used?
  - What endpoint URL is called?
  - How is `apiClient` configured?

- [ ] **Step 4:** Open `frontend/src/api/client.ts` line 7
  - What's the base URL?
  - Find the request interceptor (line 14) - what does it add to headers?
  - Find the response interceptor (line 28) - what happens on 401 error?

- [ ] **Step 5:** Open `backend/app/api/v1/auth.py` line 83
  - Find the `login` endpoint
  - What are the 3 `Depends()` doing? (Hint: dependency injection)
  - How is the password verified? (Check `security.py`)

- [ ] **Step 6:** Open `backend/app/core/security.py` line 15
  - How does `verify_password` work?
  - What hashing algorithm is used? (Hint: line 12)

- [ ] **Step 7:** Back in `auth.py` line 110
  - How is the JWT token created?
  - What data goes into the token payload?
  - How long until it expires?

- [ ] **Step 8:** Draw the complete flow diagram
  ```
  Login.tsx → [YOUR DIAGRAM HERE] → Database → Response
  ```

#### Verification:

```bash
# Test the login flow
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Should return: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
```

<details>
<summary>💡 Hint: Understanding Dependency Injection</summary>

`Depends(get_current_user)` is FastAPI's dependency injection. It automatically:
1. Runs `get_current_user` function BEFORE the endpoint
2. Passes the return value as the `current_user` parameter
3. If `get_current_user` raises an exception, the endpoint never runs

This is how authentication works - every protected endpoint has `Depends(get_current_user)` which validates the JWT token.
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Add a `console.log` at each step of the login flow (frontend only) to see the data transformations:
- Form data
- API request
- API response
- Stored token
- User object
</details>

---

### Exercise 1.2: Understand Async/Await

**Objective:** See why async is used and how it improves performance

**Why This Matters:** This entire backend is async. Understanding when to use `await` vs when not to is crucial for writing correct code.

**Files to Read:**
- `backend/app/services/canvas_service.py:163-190`
- `backend/app/api/v1/canvas.py:167-220`

#### Tasks:

- [ ] **Step 1:** Open `canvas_service.py` line 163
  - Read the `get_all_assignments` function
  - What does `asyncio.gather(*tasks)` do?
  - Why is this better than a `for` loop?

- [ ] **Step 2:** Calculate the performance difference
  ```python
  # Sequential (slow)
  for course in courses:  # 10 courses
      assignments = await get_assignments(course)  # 2 seconds each
  # Total: 20 seconds

  # Concurrent (fast)
  tasks = [get_assignments(course) for course in courses]
  results = await asyncio.gather(*tasks)
  # Total: 2 seconds (all run at same time!)
  ```

- [ ] **Step 3:** Find an example of WRONG async usage
  - Look at `canvas_service.py` line 73-117
  - Why is line 87 using a regular `for` loop instead of async?
  - Hint: Check what `_process_page` does - is it an async function?

#### Verification:

Answer these questions:
1. When should you use `await`?
2. When should you use `asyncio.gather()`?
3. What happens if you forget `await`?

<details>
<summary>💡 Hint: Async Rules</summary>

**Rule 1:** Only use `await` inside `async def` functions
**Rule 2:** Always `await` async function calls (or you get a coroutine object, not the result)
**Rule 3:** Use `asyncio.gather()` to run multiple async operations concurrently
**Rule 4:** Regular (sync) functions in an async function are fine - no `await` needed
</details>

---

### Exercise 1.3: Trace Database Queries

**Objective:** Understand how SQLAlchemy async queries work

**Why This Matters:** All database operations use async SQLAlchemy. You need to understand the pattern: execute → scalar/scalars → all/one

**Starting Point:** `backend/app/api/v1/assignments.py:85-110`

#### Tasks:

- [ ] **Step 1:** Find the `list_assignments` function
  - What does `select(Assignment).where(...)` create? (Hint: not executed yet)
  - When is the query actually executed?

- [ ] **Step 2:** Understand the execution pattern
  ```python
  query = select(Assignment).where(Assignment.user_id == current_user.id)
  # ↑ This is just a query object, nothing sent to DB yet

  result = await db.execute(query)
  # ↑ NOW the query is sent to database

  assignments = result.scalars().all()
  # ↑ Convert result to list of Assignment objects
  ```

- [ ] **Step 3:** Open `backend/app/core/deps.py` line 32
  - Read the `get_db` function
  - What is `AsyncGenerator` doing?
  - Why does it `yield` instead of `return`?
  - What happens on error? (Hint: rollback)

- [ ] **Step 4:** Find a relationship query
  - Open `backend/app/models/user.py` line 38
  - See `assignments = relationship(...)`
  - How do you access a user's assignments? (Hint: `user.assignments`)

#### SQL Understanding:

For this query in `assignments.py`:
```python
query = select(Assignment)\
    .where(Assignment.user_id == current_user.id)\
    .where(Assignment.is_completed == False)\
    .order_by(Assignment.due_date)

result = await db.execute(query)
assignments = result.scalars().all()
```

What SQL is generated?

<details>
<summary>💡 Hint: Generated SQL</summary>

```sql
SELECT * FROM assignments
WHERE user_id = $1 AND is_completed = false
ORDER BY due_date;
```

The `$1` is a parameter (SQLAlchemy prevents SQL injection automatically).
</details>

#### Verification:

Write a simple query to get all completed assignments for a user:

```python
@router.get("/completed")
async def get_completed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # YOUR CODE HERE
    pass
```

<details>
<summary>🎯 Stretch Goal</summary>

Enable SQL logging to see actual queries:
1. Open `backend/app/db/session.py` line 11
2. Change `echo=settings.DEBUG` to `echo=True`
3. Restart backend
4. Make an API call - you'll see SQL in terminal!
</details>

---

## Module 2: Backend Improvements (Estimated: 4-6 hours)

### Exercise 2.1: Add Password Strength Validation 🔒

**Objective:** Add Pydantic validators to enforce strong passwords

**Why This Matters:** Right now any password is accepted. This is a security risk. You'll learn Pydantic field validators - a pattern used throughout the codebase for data validation.

**Files to Modify:**
- `backend/app/api/v1/auth.py:21-25` (UserRegister schema)

#### Current Problem:

```python
class UserRegister(BaseModel):
    email: EmailStr  # ✅ Email validated
    password: str    # ❌ ANY string accepted (even "1" or "")
    full_name: str | None = None
```

#### Tasks:

- [ ] **Step 1:** Add password length validation
  ```python
  from pydantic import field_validator

  class UserRegister(BaseModel):
      email: EmailStr
      password: str
      full_name: str | None = None

      @field_validator('password')
      @classmethod
      def password_strength(cls, v: str) -> str:
          if len(v) < 8:
              raise ValueError('Password must be at least 8 characters')
          # Add more checks
          return v
  ```

- [ ] **Step 2:** Add these password requirements:
  - At least one uppercase letter
  - At least one number
  - At least one special character (!@#$%^&*)

- [ ] **Step 3:** Add a helpful error message
  ```python
  if not any(c.isupper() for c in v):
      raise ValueError('Password must contain at least one uppercase letter')
  ```

#### Verification:

```bash
# Test weak password (should fail)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"weak"}'

# Should return: {"detail": [{"loc": ["body","password"], "msg": "Password must be at least 8 characters"}]}

# Test strong password (should succeed)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@test.com","password":"Strong123!@#"}'
```

<details>
<summary>💡 Hint: Checking for Characters</summary>

```python
# Check for uppercase
any(c.isupper() for c in password)

# Check for numbers
any(c.isdigit() for c in password)

# Check for special characters
any(c in '!@#$%^&*' for c in password)
```
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Add a `PasswordField` custom type that can be reused:

```python
# app/core/validators.py
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

class PasswordField(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema()
        )

    @classmethod
    def _validate(cls, v: str) -> str:
        # All validation logic here
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # ... more checks
        return v

# Usage in schema:
class UserRegister(BaseModel):
    password: PasswordField  # Automatically validated!
```
</details>

---

### Exercise 2.2: Fix Error Handling in Services 🐛

**Objective:** Replace generic exception catching with specific error types

**Why This Matters:** Right now services use `except Exception` and `print()` - this makes debugging impossible in production. You'll learn proper error handling with custom exceptions and logging.

**Files to Modify:**
- `backend/app/services/canvas_service.py:73-117`

#### Current Problem:

```python
try:
    # ... API call
    return courses
except Exception as e:
    print(f"Error: {e}")  # ❌ Goes to console, lost in production
    return []  # ❌ Silently fails - caller can't tell if no courses or error
```

#### Tasks:

- [ ] **Step 1:** Create custom exception classes
  - Create file: `backend/app/services/exceptions.py`
  ```python
  class ServiceError(Exception):
      """Base exception for service layer errors."""
      pass

  class CanvasServiceError(ServiceError):
      """Canvas service errors."""
      pass

  class CanvasAuthError(CanvasServiceError):
      """Canvas authentication failed."""
      pass

  class CanvasNetworkError(CanvasServiceError):
      """Network error communicating with Canvas."""
      pass
  ```

- [ ] **Step 2:** Replace `print()` with `logging`
  ```python
  import logging
  logger = logging.getLogger(__name__)

  # Replace this:
  print(f"Error: {e}")

  # With this:
  logger.error(f"Error fetching Canvas courses: {e}", exc_info=True)
  ```

- [ ] **Step 3:** Catch specific exceptions in `canvas_service.py:73-117`
  ```python
  import httpx
  from app.services.exceptions import CanvasAuthError, CanvasNetworkError

  async def get_courses(self, enrollment_state: str = "active"):
      try:
          # ... API call
      except httpx.HTTPStatusError as e:
          if e.response.status_code == 401:
              logger.error("Canvas authentication failed")
              raise CanvasAuthError("Invalid Canvas API token")
          elif e.response.status_code >= 500:
              logger.error(f"Canvas server error: {e}")
              raise CanvasServiceError(f"Canvas API error: {e}")
          raise
      except httpx.RequestError as e:
          logger.error(f"Network error: {e}")
          raise CanvasNetworkError(f"Could not connect to Canvas: {e}")
  ```

- [ ] **Step 4:** Handle these exceptions in the API endpoint
  - Open `backend/app/api/v1/canvas.py:167`
  - Wrap the Canvas sync in try/except
  ```python
  from app.services.exceptions import CanvasAuthError, CanvasNetworkError

  try:
      # ... canvas sync logic
  except CanvasAuthError:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Canvas authentication failed. Please check your API token."
      )
  except CanvasNetworkError as e:
      raise HTTPException(
          status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
          detail=f"Could not connect to Canvas: {str(e)}"
      )
  ```

#### Verification:

```bash
# Test with invalid Canvas token (should get clear error)
curl -X POST http://localhost:8000/api/v1/canvas/sync \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Should return:
# {"detail": "Canvas authentication failed. Please check your API token."}
# NOT empty array or generic error
```

<details>
<summary>💡 Hint: When to Catch Exceptions</summary>

**Catch at the API boundary:**
- Convert service exceptions → HTTP exceptions
- Give user-friendly error messages
- Log the details for debugging

**Don't catch in the middle:**
- Let exceptions bubble up
- Only catch if you can handle it meaningfully
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Add structured logging with context:

```python
logger.error(
    "Canvas API error",
    extra={
        "user_id": current_user.id,
        "endpoint": request.url.path,
        "status_code": e.response.status_code,
        "response_body": e.response.text[:200]  # First 200 chars
    }
)
```
</details>

---

### Exercise 2.3: Add Input Validation to Assignments 📝

**Objective:** Add Pydantic validators to prevent bad data

**Why This Matters:** Right now you can create an assignment with a 10,000 character title or a due date in the past. Learning validators prevents bugs and improves UX.

**Files to Modify:**
- `backend/app/api/v1/assignments.py:20-26`

#### Current Problem:

```python
class AssignmentCreate(BaseModel):
    title: str  # ❌ No length limit
    description: str | None = None
    course_name: str  # ❌ Could be empty or SQL injection attempt
    assignment_type: str  # ❌ Could be anything ("asdfgh")
    due_date: datetime  # ❌ Could be 1900 or in the past
```

#### Tasks:

- [ ] **Step 1:** Add title validation
  ```python
  from pydantic import field_validator

  @field_validator('title')
  @classmethod
  def title_must_be_reasonable(cls, v: str) -> str:
      v = v.strip()
      if len(v) < 3:
          raise ValueError('Title must be at least 3 characters')
      if len(v) > 200:
          raise ValueError('Title must be less than 200 characters')
      return v
  ```

- [ ] **Step 2:** Add assignment type validation
  ```python
  @field_validator('assignment_type')
  @classmethod
  def assignment_type_must_be_valid(cls, v: str) -> str:
      valid_types = ['homework', 'exam', 'project', 'essay', 'discussion', 'quiz', 'lab']
      if v.lower() not in valid_types:
          raise ValueError(f'Assignment type must be one of: {", ".join(valid_types)}')
      return v.lower()
  ```

- [ ] **Step 3:** Add due date validation
  ```python
  from datetime import datetime, timedelta

  @field_validator('due_date')
  @classmethod
  def due_date_must_be_reasonable(cls, v: datetime) -> datetime:
      now = datetime.utcnow()
      if v < now - timedelta(days=1):
          raise ValueError('Due date cannot be more than 1 day in the past')
      if v > now + timedelta(days=365):
          raise ValueError('Due date cannot be more than 1 year in the future')
      return v
  ```

- [ ] **Step 4:** Sanitize course name
  ```python
  @field_validator('course_name')
  @classmethod
  def course_name_must_be_clean(cls, v: str) -> str:
      v = v.strip()
      if len(v) < 2:
          raise ValueError('Course name must be at least 2 characters')
      if len(v) > 100:
          raise ValueError('Course name must be less than 100 characters')
      # Remove potentially dangerous characters
      dangerous_chars = ['<', '>', ';', '--', '/*', '*/']
      for char in dangerous_chars:
          if char in v:
              raise ValueError('Course name contains invalid characters')
      return v
  ```

#### Verification:

```bash
# Test validation (should fail)
curl -X POST http://localhost:8000/api/v1/assignments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ab",
    "course_name": "CS",
    "assignment_type": "invalid",
    "due_date": "2020-01-01T00:00:00Z"
  }'

# Should return validation errors for each field
```

<details>
<summary>💡 Hint: Better Assignment Types</summary>

Instead of string validation, use an Enum:

```python
from enum import Enum

class AssignmentType(str, Enum):
    HOMEWORK = "homework"
    EXAM = "exam"
    PROJECT = "project"
    ESSAY = "essay"
    DISCUSSION = "discussion"
    QUIZ = "quiz"
    LAB = "lab"

class AssignmentCreate(BaseModel):
    assignment_type: AssignmentType  # Automatic validation!
```
</details>

---

## Module 3: Database & Models (Estimated: 3-4 hours)

### Exercise 3.1: Create a Database Migration 🗄️

**Objective:** Add a new field to assignments table

**Why This Matters:** You'll learn Alembic migrations - how to evolve your database schema safely. This is essential for production apps.

**Goal:** Add a `priority` field to assignments (1=high, 2=medium, 3=low)

#### Tasks:

- [ ] **Step 1:** Modify the Assignment model
  - Open `backend/app/models/assignment.py:34`
  - Add after `completion_percentage`:
  ```python
  priority = Column(Integer, default=2, nullable=False)  # 1=high, 2=medium, 3=low
  ```

- [ ] **Step 2:** Create migration file manually
  - Create: `backend/alembic/versions/002_add_assignment_priority.py`
  ```python
  """add assignment priority

  Revision ID: 002_add_priority
  Revises: 001_add_tasks
  Create Date: 2025-11-24
  """
  from alembic import op
  import sqlalchemy as sa

  revision = '002_add_priority'
  down_revision = '001_add_tasks'
  branch_labels = None
  depends_on = None

  def upgrade():
      """Add priority column to assignments."""
      op.add_column('assignments',
          sa.Column('priority', sa.Integer(), nullable=False, server_default='2')
      )

  def downgrade():
      """Remove priority column."""
      op.drop_column('assignments', 'priority')
  ```

- [ ] **Step 3:** Run the migration
  ```bash
  cd backend
  alembic upgrade head

  # Should see: "Running upgrade 001_add_tasks -> 002_add_priority, add assignment priority"
  ```

- [ ] **Step 4:** Verify in database
  ```bash
  psql $DATABASE_URL
  \d assignments
  # Should see new 'priority' column
  ```

- [ ] **Step 5:** Update the Pydantic schemas
  - Open `backend/app/api/v1/assignments.py:20`
  - Add to `AssignmentCreate`:
  ```python
  priority: int = 2  # Default to medium priority

  @field_validator('priority')
  @classmethod
  def priority_must_be_valid(cls, v: int) -> int:
      if v not in [1, 2, 3]:
          raise ValueError('Priority must be 1 (high), 2 (medium), or 3 (low)')
      return v
  ```

  - Add to `AssignmentResponse` (line 41):
  ```python
  priority: int
  ```

#### Verification:

```bash
# Create assignment with priority
curl -X POST http://localhost:8000/api/v1/assignments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High Priority Exam",
    "course_name": "CS 101",
    "assignment_type": "exam",
    "due_date": "2025-12-15T10:00:00Z",
    "priority": 1
  }'

# Should return assignment with priority: 1
```

<details>
<summary>💡 Hint: Migration Best Practices</summary>

**Always provide defaults for new columns:**
- Use `server_default` for database-level default
- Use `nullable=True` or provide a default value
- Otherwise migration fails if table has existing rows

**Test rollback:**
```bash
alembic downgrade -1  # Undo last migration
alembic upgrade head  # Redo it
```
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Create an enum for priority instead of raw integers:

```python
# app/models/assignment.py
from enum import Enum

class Priority(int, Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class Assignment(Base):
    # Instead of:
    priority = Column(Integer, default=2)

    # Use:
    from sqlalchemy import Enum as SQLEnum
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
```
</details>

---

### Exercise 3.2: Understand Model Relationships 🔗

**Objective:** Learn how SQLAlchemy relationships work

**Why This Matters:** Relationships let you traverse data (like `user.assignments`) without writing JOIN queries. This is core to ORMs.

**Files to Read:**
- `backend/app/models/user.py:38-48`
- `backend/app/models/assignment.py:74-80`
- `backend/app/models/task.py:36-38`

#### Tasks:

- [ ] **Step 1:** Understand bidirectional relationships
  - Open `user.py:38` - see `assignments = relationship("Assignment", back_populates="user")`
  - Open `assignment.py:78` - see `user = relationship("User", back_populates="assignments")`
  - Why are both needed? What's `back_populates`?

- [ ] **Step 2:** Test relationship access
  - Open `backend/app/core/deps.py:44`
  - After getting user, try:
  ```python
  # This works without extra query!
  user_assignments = user.assignments  # Returns list of Assignment objects

  # Can also go backwards
  first_assignment = user.assignments[0]
  assignment_user = first_assignment.user  # Returns User object
  ```

- [ ] **Step 3:** Understand cascade delete
  - Look at `user.py:38` - see `cascade="all, delete-orphan"`
  - What happens if you delete a user?
  - Test it:
  ```python
  # Delete user
  await db.delete(user)
  await db.commit()
  # ALL their assignments, tasks, courses are also deleted!
  ```

- [ ] **Step 4:** Understand lazy loading
  - By default, relationships are lazy loaded
  - `user.assignments` triggers a second query
  - For eager loading:
  ```python
  from sqlalchemy.orm import selectinload

  result = await db.execute(
      select(User)
      .options(selectinload(User.assignments))
      .where(User.id == user_id)
  )
  user = result.scalar_one()
  # Now user.assignments is already loaded, no extra query!
  ```

#### Diagram the Relationships:

```
User
  ├── assignments (one-to-many)
  ├── tasks (one-to-many)
  ├── courses (one-to-many)
  └── credentials (one-to-many)

Assignment
  ├── user (many-to-one)
  ├── course (many-to-one)
  └── tasks (one-to-many)

Task
  ├── user (many-to-one)
  └── assignment (many-to-one)
```

<details>
<summary>💡 Hint: Relationship Quiz</summary>

**Q1:** If you delete an assignment, what happens to its tasks?
**A1:** They're deleted too (cascade)

**Q2:** If you delete a course, what happens to assignments?
**A2:** Look at `assignment.py:79` - `cascade="all, delete-orphan"` means they're deleted

**Q3:** How do you prevent cascade delete?
**A3:** Remove `cascade="all, delete-orphan"` or use `cascade="save-update"` only
</details>

---

### Exercise 3.3: Write an Advanced Query 🔍

**Objective:** Query across relationships with filters and joins

**Why This Matters:** Real apps need complex queries. You'll learn JOIN, aggregation, and filtering across tables.

**Goal:** Get all high-priority tasks due in the next 7 days for a specific course

**Files to Modify:**
- Create new endpoint in `backend/app/api/v1/tasks.py`

#### Tasks:

- [ ] **Step 1:** Write the query using relationships
  ```python
  from datetime import datetime, timedelta

  @router.get("/upcoming-urgent")
  async def get_upcoming_urgent_tasks(
      course_name: str,
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ):
      """Get high-priority tasks due in next 7 days for a course."""

      # YOUR CODE HERE
      # Hints:
      # 1. Join Task with Assignment
      # 2. Filter by user_id, priority, due_date, course_name
      # 3. Order by due_date
  ```

- [ ] **Step 2:** Solution with explicit join
  ```python
  from sqlalchemy import and_

  now = datetime.utcnow()
  week_from_now = now + timedelta(days=7)

  query = (
      select(Task)
      .join(Assignment)  # Join tasks with assignments
      .where(
          and_(
              Task.user_id == current_user.id,
              Task.priority == 1,  # High priority only
              Task.due_date >= now,
              Task.due_date <= week_from_now,
              Task.is_completed == False,
              Assignment.course_name == course_name
          )
      )
      .order_by(Task.due_date)
  )

  result = await db.execute(query)
  tasks = result.scalars().all()

  return tasks
  ```

- [ ] **Step 3:** Add to response: assignment details
  ```python
  # For each task, also return assignment title and course
  tasks_with_context = []
  for task in tasks:
      # Fetch assignment (or use joinedload)
      result = await db.execute(
          select(Assignment).where(Assignment.id == task.assignment_id)
      )
      assignment = result.scalar_one()

      tasks_with_context.append({
          "task": task,
          "assignment_title": assignment.title,
          "course_name": assignment.course_name
      })

  return tasks_with_context
  ```

- [ ] **Step 4:** Optimize with joinedload
  ```python
  from sqlalchemy.orm import joinedload

  # This loads task AND assignment in ONE query
  query = (
      select(Task)
      .options(joinedload(Task.assignment))  # ← Eager load
      .join(Assignment)
      .where(/* same filters */)
  )

  result = await db.execute(query)
  tasks = result.unique().scalars().all()

  # Now task.assignment is already loaded!
  for task in tasks:
      print(task.assignment.title)  # No extra query
  ```

#### Verification:

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/upcoming-urgent?course_name=CS%20101" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return tasks matching criteria
```

<details>
<summary>💡 Hint: Join Types</summary>

**Implicit join (via relationship):**
```python
select(Task).where(Task.assignment.has(Assignment.course_name == "CS 101"))
```

**Explicit join:**
```python
select(Task).join(Assignment).where(Assignment.course_name == "CS 101")
```

**Both work, but explicit is clearer for complex queries.**
</details>

<details>
<summary>🎯 Stretch Goal: Aggregation</summary>

Add a count of tasks per course:

```python
from sqlalchemy import func

query = (
    select(
        Assignment.course_name,
        func.count(Task.id).label('task_count')
    )
    .join(Task)
    .where(Task.user_id == current_user.id)
    .group_by(Assignment.course_name)
)

result = await db.execute(query)
course_stats = result.all()

# Returns: [("CS 101", 5), ("Math 202", 3), ...]
```
</details>

---

## Module 4: Frontend Improvements (Estimated: 4-5 hours)

### Exercise 4.1: Add Loading Skeleton 💀

**Objective:** Replace loading spinner with skeleton screens

**Why This Matters:** Skeletons improve perceived performance and UX. You'll learn conditional rendering and Tailwind patterns.

**Files to Modify:**
- `frontend/src/pages/Tasks.tsx:159-165`

#### Current State:

```tsx
{isLoading ? (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading tasks...</p>
    </div>
  </div>
) : /* actual content */}
```

#### Tasks:

- [ ] **Step 1:** Create a skeleton component
  - Create: `frontend/src/components/TaskSkeleton.tsx`
  ```tsx
  export function TaskSkeleton() {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="flex gap-2">
          <div className="h-6 bg-gray-200 rounded w-16"></div>
          <div className="h-6 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
    );
  }
  ```

- [ ] **Step 2:** Use it in Tasks page
  ```tsx
  import { TaskSkeleton } from '../components/TaskSkeleton';

  {isLoading ? (
    <div className="space-y-4">
      <TaskSkeleton />
      <TaskSkeleton />
      <TaskSkeleton />
    </div>
  ) : (
    // actual tasks
  )}
  ```

- [ ] **Step 3:** Make skeleton match actual task card
  - Look at actual task card (line 196-235)
  - Skeleton should have same structure
  ```tsx
  export function TaskSkeleton() {
    return (
      <div className="card">
        {/* Assignment header */}
        <div className="mb-4 pb-3 border-b border-gray-200">
          <div className="h-5 bg-gray-200 rounded w-1/3 mb-2 animate-pulse"></div>
          <div className="h-3 bg-gray-200 rounded w-1/4 animate-pulse"></div>
        </div>

        {/* Task items (3 skeletons) */}
        {[1, 2, 3].map(i => (
          <div key={i} className="flex items-start gap-3 p-3 mb-2">
            <div className="w-5 h-5 bg-gray-200 rounded-full animate-pulse"></div>
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2 animate-pulse"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }
  ```

#### Verification:

1. Slow down your network:
   - Chrome DevTools → Network → Throttling → Slow 3G
2. Refresh Tasks page
3. Should see skeleton animation before data loads

<details>
<summary>💡 Hint: Skeleton Best Practices</summary>

**Match the structure:**
- Same layout as real content
- Same padding/margins
- Same number of items (or reasonable estimate)

**Use animate-pulse:**
```tsx
<div className="animate-pulse">
  {/* Tailwind's built-in pulse animation */}
</div>
```

**Vary widths:**
```tsx
<div className="h-4 bg-gray-200 rounded w-3/4"></div>  {/* 75% */}
<div className="h-4 bg-gray-200 rounded w-1/2"></div>  {/* 50% */}
<div className="h-4 bg-gray-200 rounded w-2/3"></div>  {/* 66% */}
```
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Create a generic `<Skeleton>` component:

```tsx
// components/Skeleton.tsx
interface SkeletonProps {
  width?: string;
  height?: string;
  className?: string;
}

export function Skeleton({ width = 'w-full', height = 'h-4', className = '' }: SkeletonProps) {
  return (
    <div className={`bg-gray-200 rounded animate-pulse ${width} ${height} ${className}`} />
  );
}

// Usage:
<Skeleton width="w-3/4" height="h-6" />
<Skeleton width="w-1/2" height="h-4" />
```
</details>

---

### Exercise 4.2: Add Form Validation (Frontend) ✅

**Objective:** Add React Hook Form with validation to Login page

**Why This Matters:** Right now there's no client-side validation. You'll learn React Hook Form - the industry standard for forms.

**Files to Modify:**
- `frontend/src/pages/Login.tsx:15-88`

#### Current State:

```tsx
const [formData, setFormData] = useState({ email: '', password: '' });

<input
  type="email"
  value={formData.email}
  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
/>
// ❌ No validation, lots of boilerplate
```

#### Tasks:

- [ ] **Step 1:** Install React Hook Form
  ```bash
  cd frontend
  npm install react-hook-form @hookform/resolvers zod
  ```

- [ ] **Step 2:** Create Zod schema for validation
  ```tsx
  import { z } from 'zod';
  import { zodResolver } from '@hookform/resolvers/zod';
  import { useForm } from 'react-hook-form';

  const loginSchema = z.object({
    email: z.string()
      .min(1, 'Email is required')
      .email('Invalid email address'),
    password: z.string()
      .min(8, 'Password must be at least 8 characters'),
  });

  type LoginForm = z.infer<typeof loginSchema>;
  ```

- [ ] **Step 3:** Replace useState with useForm
  ```tsx
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  ```

- [ ] **Step 4:** Update form inputs
  ```tsx
  <form onSubmit={handleSubmit(onSubmit)}>
    <input
      type="email"
      {...register('email')}
      className={errors.email ? 'border-red-500' : 'border-gray-300'}
    />
    {errors.email && (
      <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
    )}

    <input
      type="password"
      {...register('password')}
      className={errors.password ? 'border-red-500' : 'border-gray-300'}
    />
    {errors.password && (
      <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
    )}

    <button type="submit" disabled={isSubmitting}>
      {isSubmitting ? 'Logging in...' : 'Login'}
    </button>
  </form>
  ```

#### Verification:

1. Try to submit with empty email → Should show "Email is required"
2. Try invalid email (no @) → Should show "Invalid email address"
3. Try password < 8 chars → Should show "Password must be at least 8 characters"
4. Valid data → Should submit

<details>
<summary>💡 Hint: Why React Hook Form?</summary>

**Before (manual state):**
- Lots of useState boilerplate
- Manual validation logic
- Manual error state management
- Re-renders on every keystroke

**After (React Hook Form):**
- Less code
- Declarative validation (Zod schema)
- Built-in error handling
- Optimized re-renders (uncontrolled inputs)
- TypeScript autocomplete for form fields
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Create a reusable form component:

```tsx
// components/FormField.tsx
import { UseFormRegister, FieldErrors } from 'react-hook-form';

interface FormFieldProps {
  name: string;
  label: string;
  type?: string;
  register: UseFormRegister<any>;
  errors: FieldErrors;
}

export function FormField({ name, label, type = 'text', register, errors }: FormFieldProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <input
        type={type}
        {...register(name)}
        className={`w-full px-3 py-2 border rounded-md ${
          errors[name] ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {errors[name] && (
        <p className="text-red-500 text-sm mt-1">
          {errors[name]?.message as string}
        </p>
      )}
    </div>
  );
}

// Usage:
<FormField name="email" label="Email" type="email" register={register} errors={errors} />
```
</details>

---

### Exercise 4.3: Create a Custom Hook 🪝

**Objective:** Extract common TanStack Query patterns into a reusable hook

**Why This Matters:** You'll see this pattern repeated in Tasks.tsx, Assignments.tsx, Jobs.tsx. Learning custom hooks reduces code duplication.

**Goal:** Create `useResource` hook for CRUD operations

#### Tasks:

- [ ] **Step 1:** Create the hook file
  - Create: `frontend/src/hooks/useResource.ts`
  ```tsx
  import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

  interface ResourceAPI<T> {
    getAll: () => Promise<T[]>;
    getOne: (id: number) => Promise<T>;
    create: (data: Partial<T>) => Promise<T>;
    update: (id: number, data: Partial<T>) => Promise<T>;
    delete: (id: number) => Promise<void>;
  }

  export function useResource<T>(resourceName: string, api: ResourceAPI<T>) {
    const queryClient = useQueryClient();

    // GET all
    const query = useQuery({
      queryKey: [resourceName],
      queryFn: api.getAll,
    });

    // CREATE
    const createMutation = useMutation({
      mutationFn: api.create,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: [resourceName] });
      },
    });

    // UPDATE
    const updateMutation = useMutation({
      mutationFn: ({ id, data }: { id: number; data: Partial<T> }) =>
        api.update(id, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: [resourceName] });
      },
    });

    // DELETE
    const deleteMutation = useMutation({
      mutationFn: api.delete,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: [resourceName] });
      },
    });

    return {
      data: query.data,
      isLoading: query.isLoading,
      error: query.error,
      create: createMutation.mutate,
      update: (id: number, data: Partial<T>) =>
        updateMutation.mutate({ id, data }),
      delete: deleteMutation.mutate,
      isCreating: createMutation.isPending,
      isUpdating: updateMutation.isPending,
      isDeleting: deleteMutation.isPending,
    };
  }
  ```

- [ ] **Step 2:** Use it in Tasks page
  ```tsx
  import { useResource } from '../hooks/useResource';
  import { tasksApi, Task } from '../api/tasks';

  export default function Tasks() {
    const {
      data: tasks,
      isLoading,
      update,
      delete: deleteTask
    } = useResource<Task>('tasks', {
      getAll: () => tasksApi.getAllTasks('pending'),
      getOne: tasksApi.getTask,  // If this endpoint exists
      create: tasksApi.createTask,  // If this endpoint exists
      update: tasksApi.updateTask,
      delete: tasksApi.deleteTask,
    });

    // Now use it:
    <button onClick={() => update(task.id, { is_completed: true })}>
      Complete
    </button>
  }
  ```

- [ ] **Step 3:** Add optimistic updates
  ```tsx
  // Enhance updateMutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<T> }) =>
      api.update(id, data),

    // Optimistic update (UI updates before server response)
    onMutate: async ({ id, data }) => {
      // Cancel ongoing queries
      await queryClient.cancelQueries({ queryKey: [resourceName] });

      // Snapshot current value
      const previous = queryClient.getQueryData<T[]>([resourceName]);

      // Optimistically update
      queryClient.setQueryData<T[]>([resourceName], (old) =>
        old?.map(item =>
          (item as any).id === id ? { ...item, ...data } : item
        )
      );

      return { previous };
    },

    // Rollback on error
    onError: (err, variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData([resourceName], context.previous);
      }
    },

    // Always refetch
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [resourceName] });
    },
  });
  ```

#### Verification:

1. Replace query logic in Tasks.tsx with `useResource`
2. Click checkbox to complete task
3. Task should gray out IMMEDIATELY (optimistic)
4. If server fails, it reverts
5. Less code than before!

<details>
<summary>💡 Hint: When to Use Custom Hooks</summary>

**Create a custom hook when:**
- Same logic used in 3+ places
- Logic is complex enough to test independently
- Want to encapsulate state + effects together

**Example patterns:**
- `useAuth()` - Authentication logic
- `useDebounce()` - Debounced values
- `useLocalStorage()` - localStorage sync
- `usePagination()` - Pagination logic
</details>

---

## Module 5: Security & Production Readiness (Estimated: 3-4 hours)

### Exercise 5.1: Add Rate Limiting 🚦

**Objective:** Protect API from abuse with rate limiting

**Why This Matters:** Without rate limiting, someone can spam your API causing DoS. You'll learn middleware and slowapi.

**Files to Modify:**
- `backend/app/main.py`
- `backend/app/api/v1/auth.py`

#### Tasks:

- [ ] **Step 1:** Install slowapi
  ```bash
  cd backend
  pip install slowapi
  pip freeze > requirements.txt  # Update requirements
  ```

- [ ] **Step 2:** Configure in main.py
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  from slowapi.errors import RateLimitExceeded

  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  ```

- [ ] **Step 3:** Add to sensitive endpoints
  ```python
  # In auth.py
  from app.main import limiter

  @router.post("/login")
  @limiter.limit("5/minute")  # Max 5 login attempts per minute
  async def login(...):
      # ...

  @router.post("/register")
  @limiter.limit("3/hour")  # Max 3 registrations per hour
  async def register(...):
      # ...
  ```

- [ ] **Step 4:** Add to expensive operations
  ```python
  # In canvas.py
  @router.post("/sync")
  @limiter.limit("10/hour")  # Only 10 Canvas syncs per hour
  async def sync_canvas(...):
      # ...

  # In jobs.py
  @router.post("/scrape")
  @limiter.limit("20/hour")  # Only 20 job scrapes per hour
  async def scrape_jobs(...):
      # ...
  ```

#### Verification:

```bash
# Test login rate limit
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
done

# After 5 attempts, should see:
# {"detail": "Rate limit exceeded: 5 per 1 minute"}
```

<details>
<summary>💡 Hint: Rate Limit Strategies</summary>

**By IP address (default):**
```python
Limiter(key_func=get_remote_address)
```

**By user ID (for authenticated endpoints):**
```python
def get_user_id(request: Request):
    # Extract user ID from JWT token
    return request.state.user_id

Limiter(key_func=get_user_id)
```

**Different limits for different users:**
```python
@limiter.limit("100/hour", key_func=lambda: "premium_user" if is_premium() else "free_user")
```
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Add custom error response:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "detail": f"You've exceeded the rate limit of {exc.detail}",
            "retry_after": 60  # seconds
        },
        headers={"Retry-After": "60"}
    )
```
</details>

---

### Exercise 5.2: Add Request Logging & Tracing 📊

**Objective:** Log all requests with unique IDs for debugging

**Why This Matters:** In production, you need to trace requests through the system. You'll learn middleware and structured logging.

**Files to Create/Modify:**
- Create `backend/app/middleware/logging.py`
- Modify `backend/app/main.py`

#### Tasks:

- [ ] **Step 1:** Create logging middleware
  ```python
  # backend/app/middleware/logging.py
  import logging
  import time
  import uuid
  from starlette.middleware.base import BaseHTTPMiddleware
  from starlette.requests import Request

  logger = logging.getLogger(__name__)

  class RequestLoggingMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request: Request, call_next):
          # Generate unique request ID
          request_id = str(uuid.uuid4())
          request.state.request_id = request_id

          # Log request
          logger.info(
              f"Request started",
              extra={
                  "request_id": request_id,
                  "method": request.method,
                  "path": request.url.path,
                  "client_ip": request.client.host,
              }
          )

          # Time the request
          start_time = time.time()

          # Process request
          response = await call_next(request)

          # Calculate duration
          duration = time.time() - start_time

          # Log response
          logger.info(
              f"Request completed",
              extra={
                  "request_id": request_id,
                  "status_code": response.status_code,
                  "duration_ms": round(duration * 1000, 2),
              }
          )

          # Add request ID to response headers (for debugging)
          response.headers["X-Request-ID"] = request_id

          return response
  ```

- [ ] **Step 2:** Add middleware to app
  ```python
  # backend/app/main.py
  from app.middleware.logging import RequestLoggingMiddleware

  app.add_middleware(RequestLoggingMiddleware)
  ```

- [ ] **Step 3:** Use request_id in error handling
  ```python
  # In any endpoint
  @router.post("/sync")
  async def sync_canvas(
      request: Request,  # Add this
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ):
      try:
          # ... sync logic
      except Exception as e:
          logger.error(
              "Canvas sync failed",
              extra={
                  "request_id": request.state.request_id,
                  "user_id": current_user.id,
                  "error": str(e)
              },
              exc_info=True
          )
          raise
  ```

- [ ] **Step 4:** Configure structured logging
  ```python
  # backend/app/main.py
  import logging.config

  LOGGING_CONFIG = {
      'version': 1,
      'disable_existing_loggers': False,
      'formatters': {
          'json': {
              'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
              'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
          },
      },
      'handlers': {
          'console': {
              'class': 'logging.StreamHandler',
              'formatter': 'json',
              'level': 'INFO',
          },
      },
      'root': {
          'level': 'INFO',
          'handlers': ['console']
      }
  }

  logging.config.dictConfig(LOGGING_CONFIG)
  ```

#### Verification:

```bash
# Make a request
curl http://localhost:8000/api/v1/assignments -H "Authorization: Bearer TOKEN"

# Check logs - should see:
# {"asctime": "2025-11-24 ...", "request_id": "abc-123", "method": "GET", ...}
# {"asctime": "2025-11-24 ...", "request_id": "abc-123", "status_code": 200, "duration_ms": 45.2}

# Response headers should include:
# X-Request-ID: abc-123
```

<details>
<summary>💡 Hint: Why Request IDs Matter</summary>

**Problem:** User reports "error at 3:45 PM"
- Which request was that?
- Which server handled it?
- What was the user trying to do?

**Solution with Request IDs:**
1. User sees error with request_id in UI
2. Search logs for that request_id
3. See entire request flow
4. Debug the specific request

**Example log trace:**
```json
{"request_id": "abc-123", "message": "Request started", "path": "/canvas/sync"}
{"request_id": "abc-123", "message": "Fetching Canvas courses"}
{"request_id": "abc-123", "message": "ERROR: Canvas auth failed"}
{"request_id": "abc-123", "message": "Request completed", "status_code": 401}
```
</details>

---

### Exercise 5.3: Environment-Specific Configuration 🔧

**Objective:** Separate dev/staging/production configs

**Why This Matters:** Production needs different settings than development (debug off, different secrets, etc.)

**Files to Modify:**
- `backend/app/core/config.py`

#### Tasks:

- [ ] **Step 1:** Add environment detection
  ```python
  from enum import Enum
  from functools import lru_cache

  class Environment(str, Enum):
      DEVELOPMENT = "development"
      STAGING = "staging"
      PRODUCTION = "production"

  class Settings(BaseSettings):
      environment: Environment = Environment.DEVELOPMENT

      # Different defaults per environment
      @property
      def debug(self) -> bool:
          return self.environment == Environment.DEVELOPMENT

      @property
      def database_pool_size(self) -> int:
          if self.environment == Environment.PRODUCTION:
              return 50  # Larger pool for production
          return 10  # Smaller for dev
  ```

- [ ] **Step 2:** Environment-specific .env files
  ```bash
  # .env.development
  ENVIRONMENT=development
  DEBUG=true
  DATABASE_URL=postgresql://localhost/studenthub_dev
  ALLOWED_ORIGINS=["http://localhost:3000"]

  # .env.production
  ENVIRONMENT=production
  DEBUG=false
  DATABASE_URL=postgresql://production-db/studenthub
  ALLOWED_ORIGINS=["https://studenthub.com"]
  SECRET_KEY=super-secure-production-key
  ```

- [ ] **Step 3:** Load correct .env file
  ```python
  import os

  class Settings(BaseSettings):
      model_config = SettingsConfigDict(
          env_file=f".env.{os.getenv('ENVIRONMENT', 'development')}",
          env_file_encoding="utf-8",
          case_sensitive=True
      )
  ```

- [ ] **Step 4:** Add validation
  ```python
  class Settings(BaseSettings):
      # ... fields

      @model_validator(mode='after')
      def validate_production_settings(self):
          """Ensure production has secure settings."""
          if self.environment == Environment.PRODUCTION:
              if self.DEBUG:
                  raise ValueError("DEBUG must be False in production")
              if "localhost" in str(self.DATABASE_URL):
                  raise ValueError("Cannot use localhost database in production")
              if len(self.SECRET_KEY) < 32:
                  raise ValueError("SECRET_KEY too short for production")
          return self
  ```

#### Verification:

```bash
# Test development
ENVIRONMENT=development python -c "from app.core.config import settings; print(settings.debug)"
# Should print: True

# Test production
ENVIRONMENT=production python -c "from app.core.config import settings; print(settings.debug)"
# Should print: False

# Test production validation (should fail)
ENVIRONMENT=production DEBUG=true python -c "from app.core.config import settings"
# Should raise: ValueError: DEBUG must be False in production
```

<details>
<summary>💡 Hint: .env File Priority</summary>

**Loading order (first match wins):**
1. Environment variables (highest priority)
2. `.env.production` (if ENVIRONMENT=production)
3. `.env.staging` (if ENVIRONMENT=staging)
4. `.env.development` (if ENVIRONMENT=development or not set)
5. `.env` (fallback)

**Example:**
```bash
# .env.production has: DATABASE_URL=prod-db
# But environment variable overrides:
export DATABASE_URL=override-db
python app/main.py  # Uses override-db
```
</details>

---

## Module 6: Testing (Estimated: 4-5 hours)

### Exercise 6.1: Write Your First Backend Test 🧪

**Objective:** Test the login endpoint with pytest

**Why This Matters:** No tests = no confidence in refactoring. You'll learn pytest, fixtures, and async testing.

**Files to Create:**
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/tests/test_auth.py`

#### Tasks:

- [ ] **Step 1:** Install test dependencies
  ```bash
  cd backend
  pip install pytest pytest-asyncio httpx
  ```

- [ ] **Step 2:** Create test configuration
  ```python
  # backend/tests/conftest.py
  import pytest
  from httpx import AsyncClient
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
  from sqlalchemy.orm import sessionmaker

  from app.main import app
  from app.db.session import Base, get_db
  from app.core.config import settings

  # Use separate test database
  TEST_DATABASE_URL = "postgresql+asyncpg://localhost/studenthub_test"

  @pytest.fixture(scope="session")
  async def test_engine():
      """Create test database engine."""
      engine = create_async_engine(TEST_DATABASE_URL, echo=True)

      # Create all tables
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.create_all)

      yield engine

      # Drop all tables after tests
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.drop_all)

  @pytest.fixture
  async def db_session(test_engine):
      """Create a test database session."""
      async_session = sessionmaker(
          test_engine, class_=AsyncSession, expire_on_commit=False
      )

      async with async_session() as session:
          yield session

  @pytest.fixture
  async def client(db_session):
      """Create test HTTP client."""
      async def override_get_db():
          yield db_session

      app.dependency_overrides[get_db] = override_get_db

      async with AsyncClient(app=app, base_url="http://test") as ac:
          yield ac

      app.dependency_overrides.clear()
  ```

- [ ] **Step 3:** Write login tests
  ```python
  # backend/tests/test_auth.py
  import pytest
  from httpx import AsyncClient

  @pytest.mark.asyncio
  async def test_register_new_user(client: AsyncClient):
      """Test successful user registration."""
      response = await client.post(
          "/api/v1/auth/register",
          json={
              "email": "newuser@test.com",
              "password": "SecurePass123!",
              "full_name": "Test User"
          }
      )

      assert response.status_code == 201
      data = response.json()
      assert data["email"] == "newuser@test.com"
      assert "password" not in data  # Password not in response
      assert "hashed_password" not in data

  @pytest.mark.asyncio
  async def test_register_duplicate_email(client: AsyncClient):
      """Test registration with existing email fails."""
      # Register first user
      await client.post(
          "/api/v1/auth/register",
          json={
              "email": "duplicate@test.com",
              "password": "SecurePass123!"
          }
      )

      # Try to register again with same email
      response = await client.post(
          "/api/v1/auth/register",
          json={
              "email": "duplicate@test.com",
              "password": "DifferentPass123!"
          }
      )

      assert response.status_code == 400
      assert "already registered" in response.json()["detail"].lower()

  @pytest.mark.asyncio
  async def test_login_success(client: AsyncClient):
      """Test successful login."""
      # Register user
      await client.post(
          "/api/v1/auth/register",
          json={
              "email": "login@test.com",
              "password": "SecurePass123!"
          }
      )

      # Login
      response = await client.post(
          "/api/v1/auth/login",
          json={
              "email": "login@test.com",
              "password": "SecurePass123!"
          }
      )

      assert response.status_code == 200
      data = response.json()
      assert "access_token" in data
      assert "refresh_token" in data
      assert data["token_type"] == "bearer"

  @pytest.mark.asyncio
  async def test_login_wrong_password(client: AsyncClient):
      """Test login with wrong password fails."""
      # Register user
      await client.post(
          "/api/v1/auth/register",
          json={
              "email": "wrong@test.com",
              "password": "CorrectPass123!"
          }
      )

      # Try wrong password
      response = await client.post(
          "/api/v1/auth/login",
          json={
              "email": "wrong@test.com",
              "password": "WrongPass123!"
          }
      )

      assert response.status_code == 401
      assert "incorrect" in response.json()["detail"].lower()
  ```

- [ ] **Step 4:** Run tests
  ```bash
  cd backend

  # Create test database
  createdb studenthub_test

  # Run tests
  pytest tests/test_auth.py -v

  # Should see:
  # test_auth.py::test_register_new_user PASSED
  # test_auth.py::test_register_duplicate_email PASSED
  # test_auth.py::test_login_success PASSED
  # test_auth.py::test_login_wrong_password PASSED
  ```

#### Verification:

All tests should pass. If any fail, debug using:
```bash
pytest tests/test_auth.py -v -s  # -s shows print statements
pytest tests/test_auth.py::test_login_success -v  # Run single test
```

<details>
<summary>💡 Hint: Test Database Best Practices</summary>

**Always use a separate test database:**
- Never test against development database
- Tests should be isolated
- Tests should be repeatable

**Reset between tests:**
```python
@pytest.fixture(autouse=True)
async def reset_db(db_session):
    """Reset database after each test."""
    yield
    # Rollback any changes
    await db_session.rollback()
```

**Use transactions:**
```python
@pytest.fixture
async def db_session(test_engine):
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection)

    yield session

    await transaction.rollback()  # Rollback everything
    await connection.close()
```
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Add factory functions for test data:

```python
# tests/factories.py
from app.models.user import User
from app.core.security import get_password_hash

async def create_test_user(
    db_session,
    email="test@test.com",
    password="TestPass123!",
    **kwargs
):
    """Create a test user."""
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        **kwargs
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

# Usage in tests:
async def test_something(db_session):
    user = await create_test_user(db_session, email="specific@test.com")
    # ... test logic
```
</details>

---

### Exercise 6.2: Write Frontend Component Tests 🎭

**Objective:** Test React component with React Testing Library

**Why This Matters:** Frontend tests catch UI bugs and regressions. You'll learn component testing patterns.

**Files to Create:**
- `frontend/src/pages/__tests__/Login.test.tsx`

#### Tasks:

- [ ] **Step 1:** Install test dependencies
  ```bash
  cd frontend
  npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
  ```

- [ ] **Step 2:** Configure Vitest
  ```typescript
  // frontend/vite.config.ts
  import { defineConfig } from 'vite'
  import react from '@vitejs/plugin-react'

  export default defineConfig({
    plugins: [react()],
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
    },
  })
  ```

- [ ] **Step 3:** Create test setup
  ```typescript
  // frontend/src/test/setup.ts
  import { expect, afterEach } from 'vitest';
  import { cleanup } from '@testing-library/react';
  import * as matchers from '@testing-library/jest-dom/matchers';

  expect.extend(matchers);

  afterEach(() => {
    cleanup();
  });
  ```

- [ ] **Step 4:** Write Login component tests
  ```typescript
  // frontend/src/pages/__tests__/Login.test.tsx
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen, waitFor } from '@testing-library/react';
  import userEvent from '@testing-library/user-event';
  import { BrowserRouter } from 'react-router-dom';
  import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
  import Login from '../Login';

  // Mock auth store
  vi.mock('../../store/authStore', () => ({
    useAuthStore: () => ({
      login: vi.fn(),
      error: null,
      isLoading: false,
      clearError: vi.fn(),
    }),
  }));

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  const renderLogin = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Login />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  describe('Login', () => {
    it('renders login form', () => {
      renderLogin();

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    it('shows validation errors for empty fields', async () => {
      const user = userEvent.setup();
      renderLogin();

      // Click login without filling form
      await user.click(screen.getByRole('button', { name: /login/i }));

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
        expect(screen.getByText(/password/i)).toBeInTheDocument();
      });
    });

    it('calls login with form data on submit', async () => {
      const user = userEvent.setup();
      const { useAuthStore } = await import('../../store/authStore');
      const mockLogin = vi.fn();
      (useAuthStore as any).mockReturnValue({
        login: mockLogin,
        error: null,
        isLoading: false,
      });

      renderLogin();

      // Fill form
      await user.type(screen.getByLabelText(/email/i), 'test@test.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');

      // Submit
      await user.click(screen.getByRole('button', { name: /login/i }));

      // Should call login
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'test@test.com',
          password: 'password123',
        });
      });
    });
  });
  ```

- [ ] **Step 5:** Run tests
  ```bash
  cd frontend
  npm test

  # Or run in watch mode
  npm test -- --watch
  ```

#### Verification:

All tests should pass. Common issues:
- Missing test IDs → Add `data-testid` attributes
- Async errors → Use `waitFor()` for async operations
- Mock errors → Check vi.mock() paths

<details>
<summary>💡 Hint: Testing Best Practices</summary>

**Query priority (from docs):**
1. `getByRole` - Accessible queries (best)
2. `getByLabelText` - Form inputs
3. `getByPlaceholderText` - If no label
4. `getByText` - Non-interactive elements
5. `getByTestId` - Last resort

**Example:**
```tsx
// ✅ Good - Accessible
screen.getByRole('button', { name: /login/i })

// ❌ Bad - Implementation detail
screen.getByTestId('login-button')
```

**Use user-event instead of fireEvent:**
```tsx
// ✅ Good - Simulates real user
await user.click(button)
await user.type(input, 'text')

// ❌ Bad - Low-level
fireEvent.click(button)
```
</details>

---

## Module 7: Full-Stack Feature (Estimated: 6-8 hours)

### Exercise 7.1: Build "Mark All as Complete" Feature 🎯

**Objective:** Add a feature end-to-end (database → API → UI)

**Why This Matters:** This exercises everything you've learned. You'll see how changes flow through the entire stack.

**Goal:** Add a button to mark all pending tasks as complete at once

#### Tasks:

**BACKEND**

- [ ] **Step 1:** Add database query
  ```python
  # backend/app/api/v1/tasks.py
  @router.post("/complete-all")
  async def complete_all_tasks(
      assignment_id: int | None = None,  # Optional: complete all for one assignment
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ):
      """Mark all pending tasks as complete."""
      from sqlalchemy import update
      from datetime import datetime

      # Build query
      query = (
          update(Task)
          .where(
              Task.user_id == current_user.id,
              Task.is_completed == False
          )
          .values(
              is_completed=True,
              completed_at=datetime.utcnow()
          )
      )

      # Optional: filter by assignment
      if assignment_id:
          query = query.where(Task.assignment_id == assignment_id)

      # Execute
      result = await db.execute(query)
      updated_count = result.rowcount

      await db.commit()

      # Update assignment completion percentages
      if assignment_id:
          await update_assignment_progress(assignment_id, db)
      else:
          # Update all assignments
          result = await db.execute(
              select(Assignment.id)
              .where(Assignment.user_id == current_user.id)
          )
          assignment_ids = result.scalars().all()
          for aid in assignment_ids:
              await update_assignment_progress(aid, db)

      return {
          "status": "success",
          "message": f"Marked {updated_count} tasks as complete"
      }
  ```

- [ ] **Step 2:** Test the endpoint
  ```bash
  curl -X POST "http://localhost:8000/api/v1/tasks/complete-all" \
    -H "Authorization: Bearer YOUR_TOKEN"

  # Should return: {"status": "success", "message": "Marked 5 tasks as complete"}
  ```

**FRONTEND**

- [ ] **Step 3:** Add API method
  ```typescript
  // frontend/src/api/tasks.ts
  export const tasksApi = {
    // ... existing methods

    completeAllTasks: async (assignmentId?: number) => {
      const params = assignmentId ? { assignment_id: assignmentId } : {};
      const response = await apiClient.post('/tasks/complete-all', null, { params });
      return response.data;
    },
  };
  ```

- [ ] **Step 4:** Add UI button
  ```tsx
  // frontend/src/pages/Tasks.tsx
  import { Check } from 'lucide-react';

  const completeAllMutation = useMutation({
    mutationFn: () => tasksApi.completeAllTasks(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      alert(data.message);
    },
  });

  // In the JSX, add after filter tabs:
  <div className="flex items-center gap-2">
    {/* Existing filter tabs */}

    <button
      onClick={() => {
        if (confirm('Mark all pending tasks as complete?')) {
          completeAllMutation.mutate();
        }
      }}
      disabled={completeAllMutation.isPending || !tasks || tasks.length === 0}
      className="btn-secondary ml-auto flex items-center gap-2"
    >
      <Check className="w-4 h-4" />
      Complete All
    </button>
  </div>
  ```

- [ ] **Step 5:** Add per-assignment button
  ```tsx
  // In the assignment group header (line 188-197)
  <div className="mb-4 pb-3 border-b border-gray-200">
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">
          {group.assignment_title}
        </h3>
        {group.assignment_course && (
          <p className="text-sm text-gray-600">{group.assignment_course}</p>
        )}
      </div>

      <button
        onClick={() => {
          if (confirm(`Mark all tasks for "${group.assignment_title}" as complete?`)) {
            completeAllMutation.mutate(/* assignment_id */);
          }
        }}
        className="btn-sm btn-secondary"
      >
        Complete All
      </button>
    </div>
  </div>
  ```

#### Verification:

1. Go to /tasks page
2. Should see "Complete All" button
3. Click it → Confirmation dialog
4. Confirm → All tasks marked complete
5. Assignment completion % should update
6. Test per-assignment button too

<details>
<summary>💡 Hint: Bulk Operations</summary>

**Use SQL UPDATE for bulk operations:**
```python
# ✅ Good - Single query
update(Task).where(...).values(is_completed=True)

# ❌ Bad - N queries
for task in tasks:
    task.is_completed = True
    db.add(task)
```

**Benefits:**
- Faster (one query vs many)
- Atomic (all or nothing)
- Less memory (don't load all objects)
</details>

<details>
<summary>🎯 Stretch Goal</summary>

Add undo functionality:

```python
@router.post("/complete-all/undo")
async def undo_complete_all(
    before: datetime,  # Undo completions after this time
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Undo bulk complete operation."""
    query = (
        update(Task)
        .where(
            Task.user_id == current_user.id,
            Task.completed_at >= before
        )
        .values(
            is_completed=False,
            completed_at=None
        )
    )

    result = await db.execute(query)
    await db.commit()

    return {"undone": result.rowcount}
```
</details>

---

## Learning Journal Template 📓

Use this to track your progress and insights.

### Module 1: Architecture Understanding
**Date Completed:** _____________

**Key Learnings:**
-
-
-

**Aha Moments:**
-
-

**Questions for Later:**
-
-

---

### Module 2: Backend Improvements
**Date Completed:** _____________

**What I Built:**
-
-

**Challenges:**
-
-

**How I Solved Them:**
-
-

---

### Module 3: Database & Models
**Date Completed:** _____________

**Concepts Mastered:**
-
-

**Things I'm Still Unclear About:**
-
-

---

### Module 4: Frontend Improvements
**Date Completed:** _____________

**Components I Created/Modified:**
-
-

**React Patterns I Learned:**
-
-

---

### Module 5: Security & Production
**Date Completed:** _____________

**Security Improvements Made:**
-
-

**Production Readiness Checklist:**
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Environment configs separated
- [ ] Error handling improved
- [ ] Input validation added

---

### Module 6: Testing
**Date Completed:** _____________

**Tests Written:**
- Backend: _____ tests
- Frontend: _____ tests

**Test Coverage:**
-

**Testing Insights:**
-
-

---

### Module 7: Full-Stack Feature
**Date Completed:** _____________

**Feature Built:**
-

**Full-Stack Flow I Now Understand:**
-
-

---

## Congratulations! 🎉

You've completed all exercises and significantly improved the Student Hub codebase!

### What You've Accomplished:

✅ **Architecture Mastery**
- Traced complete request flows
- Understood async/await patterns
- Mastered dependency injection

✅ **Backend Skills**
- Fixed error handling
- Added validation
- Created migrations
- Wrote complex queries

✅ **Frontend Skills**
- Built React components
- Created custom hooks
- Implemented forms
- Added loading states

✅ **Production Readiness**
- Added rate limiting
- Implemented logging
- Separated configs
- Improved security

✅ **Testing**
- Backend API tests
- Frontend component tests
- Test-driven development

✅ **Full-Stack Development**
- Built features end-to-end
- Connected all the pieces
- Deployed changes

### Next Steps:

1. **Deploy to Production**
   - Railway (backend)
   - Vercel (frontend)
   - Test in production

2. **Add More Features**
   - Pick from `INTERN_ONBOARDING.md` polishing list
   - Build something you want to use

3. **Keep Learning**
   - Contribute to open source
   - Build your own projects
   - Teach others what you've learned

**You're now a full-stack developer! 🚀**
