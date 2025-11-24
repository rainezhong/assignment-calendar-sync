# Phase 7: Simple Task Breakdown (Simplified)

**Goal**: Automatically break assignments into tasks, viewable as calendar events or priority-ordered todo list.

---

## Simple Flow

1. **Assignment synced** (Canvas/Gradescope/Gmail) → **AI auto-generates tasks**
2. **Tasks saved to database** with priority and due dates
3. **View as calendar** - Tasks show up as events
4. **View as todo list** - Tasks ordered by priority

---

## Database Schema

### Task Model (Simple)
```python
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)

    # Task details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Priority (1 = highest, 2 = medium, 3 = low)
    priority = Column(Integer, default=2)

    # Dates
    due_date = Column(DateTime(timezone=True), nullable=False)  # When task should be done
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    is_completed = Column(Boolean, default=False)

    # Order in list
    order = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="tasks")
    user = relationship("User", back_populates="tasks")
```

---

## AI Task Generation

### Simple Prompt
```
Break down this assignment into 5-8 specific tasks:

Assignment: {title}
Course: {course_name}
Type: {assignment_type}
Description: {description}
Due Date: {due_date}

Return JSON:
{
  "tasks": [
    {
      "title": "Read assignment requirements",
      "description": "Review rubric and understand expectations",
      "priority": 1,
      "order": 0
    },
    ...
  ]
}
```

### Auto-generate triggers:
- When assignment synced from Canvas
- When assignment synced from Gradescope
- When assignment created manually

---

## API Endpoints (Simple)

```python
# Auto-generates tasks when assignment created
POST /assignments/{id}/generate-tasks

# Get all tasks for user (ordered by priority)
GET /tasks?status=pending

# Get tasks for specific assignment
GET /assignments/{id}/tasks

# Mark task complete
PATCH /tasks/{id}/complete

# Get calendar view of tasks
GET /tasks/calendar?start_date=2025-11-23&end_date=2025-12-31
```

---

## Frontend Views

### 1. Todo List Page
- Shows all pending tasks
- Ordered by: Priority (1→3), then due date
- Checkbox to mark complete
- Shows parent assignment name

### 2. Calendar View (Dashboard)
- Shows tasks as events on calendar
- Color coded by priority
- Click to mark complete

### 3. Assignment Detail Page
- Shows tasks for that assignment
- Generate button if no tasks exist

---

## Implementation Steps

1. **Backend**:
   - Create Task model
   - Migration
   - TaskGenerationService (AI call)
   - API endpoints
   - Auto-generate on assignment sync

2. **Frontend**:
   - Tasks API client
   - Todo list page
   - Integrate into calendar
   - Integrate into assignment detail

---

Let's code!
