# Phase 7: AI-Powered Task Breakdown & Todo Lists

**Status**: 📋 Planning
**Priority**: High - Core feature for making assignments actionable

---

## Feature Overview

### Problem
Students see assignments as single monolithic items:
- "Project 3 due Dec 1" feels overwhelming
- No clear roadmap of what to do
- Hard to make progress incrementally
- No sense of progress until fully complete

### Solution
AI automatically breaks down assignments into actionable subtasks:
- Clear step-by-step todo list
- Time estimates for each task
- Progress tracking (% complete)
- Order tasks by logical dependencies
- Calendar integration for task scheduling

### Example

**Before:**
```
Assignment: Implement Search Engine
Due: December 1, 2025
Status: Not started
```

**After:**
```
Assignment: Implement Search Engine
Due: December 1, 2025
Progress: 30% complete (3/10 tasks done)

Todo List:
  ✅ Set up project repository (30 min) - Completed Nov 20
  ✅ Implement web crawler (3 hours) - Completed Nov 21
  ✅ Build inverted index (4 hours) - Completed Nov 22
  ⏳ Implement PageRank algorithm (3 hours) - In Progress
  ⬜ Create search interface (2 hours)
  ⬜ Write test cases (2 hours)
  ⬜ Write documentation (1 hour)
  ⬜ Submit on Canvas (15 min)

Total estimated time: 15.75 hours
Time remaining: 8 days (Nov 23 - Dec 1)
Recommended pace: 1.5 hours/day
```

---

## Architecture Design

### 1. Database Schema

#### New Model: `Task`
```python
# backend/app/models/task.py
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Task details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)  # Order in the list (0, 1, 2...)

    # Status tracking
    status = Column(String, default="pending")  # pending, in_progress, completed, skipped
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Time estimates (in minutes)
    estimated_minutes = Column(Integer, nullable=True)
    actual_minutes = Column(Integer, nullable=True)

    # Scheduling
    scheduled_date = Column(DateTime(timezone=True), nullable=True)  # When student plans to work on it

    # AI metadata
    category = Column(String, nullable=True)  # "setup", "implementation", "testing", "documentation", "submission"
    difficulty = Column(String, nullable=True)  # "easy", "medium", "hard"
    dependencies = Column(JSON, default=list)  # List of task IDs that must be completed first

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="tasks")
    user = relationship("User", back_populates="tasks")
```

#### Update `Assignment` Model
```python
# Add to Assignment model
tasks = relationship("Task", back_populates="assignment", cascade="all, delete-orphan")
tasks_generated = Column(Boolean, default=False)  # Track if tasks have been generated
tasks_generated_at = Column(DateTime(timezone=True), nullable=True)
```

#### Update `User` Model
```python
# Add to User model
tasks = relationship("Task", back_populates="user")
```

### 2. AI Task Generation Service

#### Service: `TaskGenerationService`
```python
# backend/app/services/task_generation_service.py

from typing import List, Dict
import anthropic  # or openai
from app.models.assignment import Assignment
from app.models.task import Task

class TaskGenerationService:
    """Generate actionable task breakdowns from assignments."""

    async def generate_tasks_for_assignment(
        self,
        assignment: Assignment,
        regenerate: bool = False
    ) -> List[Task]:
        """
        Generate a todo list breakdown for an assignment.

        Uses Claude/GPT to analyze:
        - Assignment title and description
        - Assignment type (project, essay, exam, etc.)
        - Complexity score and Bloom's level
        - Estimated hours
        - Due date (to calculate pacing)

        Returns: List of Task objects (not yet saved to DB)
        """

        # Build prompt for AI
        prompt = self._build_task_generation_prompt(assignment)

        # Call AI (Claude API)
        response = await self._call_ai_api(prompt)

        # Parse structured response
        tasks_data = self._parse_ai_response(response)

        # Create Task objects
        tasks = []
        for i, task_data in enumerate(tasks_data):
            task = Task(
                assignment_id=assignment.id,
                user_id=assignment.user_id,
                title=task_data['title'],
                description=task_data.get('description'),
                order=i,
                estimated_minutes=task_data.get('estimated_minutes'),
                category=task_data.get('category'),
                difficulty=task_data.get('difficulty'),
                dependencies=task_data.get('dependencies', []),
            )
            tasks.append(task)

        return tasks

    def _build_task_generation_prompt(self, assignment: Assignment) -> str:
        """Build AI prompt with assignment context."""

        days_until_due = (assignment.due_date - datetime.utcnow()).days

        return f"""
You are a task breakdown assistant helping students manage their coursework.

Given the following assignment, break it down into actionable subtasks:

**Assignment Details:**
- Title: {assignment.title}
- Course: {assignment.course_name}
- Type: {assignment.assignment_type}
- Description: {assignment.description or "No description provided"}
- Due Date: {assignment.due_date.strftime('%B %d, %Y')} ({days_until_due} days from now)
- Estimated Hours: {assignment.estimated_hours or "Unknown"}
- Complexity Score: {assignment.complexity_score or "Unknown"}
- Bloom's Level: {assignment.blooms_level or "Unknown"}
- Required Skills: {', '.join(assignment.required_skills) if assignment.required_skills else "None listed"}

**Instructions:**
1. Break down this assignment into 5-12 concrete, actionable tasks
2. Order tasks logically (setup → implementation → testing → submission)
3. Provide realistic time estimates for each task (in minutes)
4. Categorize each task: setup, research, implementation, testing, documentation, submission
5. Assess difficulty: easy, medium, hard
6. Consider the due date and total estimated hours

**Output Format (JSON):**
```json
{{
  "tasks": [
    {{
      "title": "Set up project repository",
      "description": "Initialize Git repo, create directory structure, set up dependencies",
      "estimated_minutes": 30,
      "category": "setup",
      "difficulty": "easy",
      "order": 0
    }},
    {{
      "title": "Implement core algorithm",
      "description": "Write the main logic for the search engine indexing",
      "estimated_minutes": 180,
      "category": "implementation",
      "difficulty": "hard",
      "order": 1
    }}
  ]
}}
```

Generate a realistic, achievable task breakdown that will help the student make steady progress.
"""

    async def _call_ai_api(self, prompt: str) -> str:
        """Call Claude/GPT API."""
        # Use existing AI service or create new one
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def _parse_ai_response(self, response: str) -> List[Dict]:
        """Parse AI response into structured task data."""
        import json

        # Extract JSON from response
        # Handle cases where AI wraps JSON in markdown code blocks
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response

        data = json.loads(json_str)
        return data.get('tasks', [])

    async def auto_schedule_tasks(
        self,
        tasks: List[Task],
        assignment: Assignment
    ) -> List[Task]:
        """
        Automatically schedule tasks across available days.

        Distributes tasks evenly from now until due date,
        respecting dependencies and difficulty.
        """

        from datetime import timedelta

        days_until_due = (assignment.due_date - datetime.utcnow()).days
        current_date = datetime.utcnow()

        # Sort by order
        sorted_tasks = sorted(tasks, key=lambda t: t.order)

        # Distribute tasks across days
        for i, task in enumerate(sorted_tasks):
            # Simple distribution: spread evenly across available days
            days_offset = int((i / len(sorted_tasks)) * days_until_due)
            task.scheduled_date = current_date + timedelta(days=days_offset)

        return sorted_tasks
```

### 3. API Endpoints

#### New Routes: `backend/app/api/v1/tasks.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

router = APIRouter()


# Pydantic schemas
class TaskResponse(BaseModel):
    id: int
    assignment_id: int
    title: str
    description: Optional[str]
    order: int
    status: str
    completed_at: Optional[datetime]
    estimated_minutes: Optional[int]
    actual_minutes: Optional[int]
    scheduled_date: Optional[datetime]
    category: Optional[str]
    difficulty: Optional[str]

    class Config:
        from_attributes = True


class GenerateTasksRequest(BaseModel):
    regenerate: bool = False  # If True, delete existing and regenerate
    auto_schedule: bool = True  # Automatically schedule across days


class UpdateTaskRequest(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    actual_minutes: Optional[int] = None
    scheduled_date: Optional[datetime] = None


# Endpoints

@router.post("/assignments/{assignment_id}/generate-tasks", response_model=List[TaskResponse])
async def generate_tasks(
    assignment_id: int,
    request: GenerateTasksRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered task breakdown for an assignment.
    """
    # Get assignment
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.user_id == current_user.id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check if tasks already exist
    result = await db.execute(
        select(Task).where(Task.assignment_id == assignment_id)
    )
    existing_tasks = result.scalars().all()

    if existing_tasks and not request.regenerate:
        raise HTTPException(
            status_code=400,
            detail="Tasks already exist. Set regenerate=true to recreate."
        )

    # Delete existing if regenerating
    if existing_tasks and request.regenerate:
        for task in existing_tasks:
            await db.delete(task)
        await db.commit()

    # Generate tasks using AI
    task_service = TaskGenerationService()
    tasks = await task_service.generate_tasks_for_assignment(assignment)

    # Auto-schedule if requested
    if request.auto_schedule:
        tasks = await task_service.auto_schedule_tasks(tasks, assignment)

    # Save to database
    for task in tasks:
        db.add(task)

    # Update assignment
    assignment.tasks_generated = True
    assignment.tasks_generated_at = datetime.utcnow()

    await db.commit()

    # Refresh to get IDs
    for task in tasks:
        await db.refresh(task)

    return tasks


@router.get("/assignments/{assignment_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks for an assignment."""
    # Verify assignment belongs to user
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.user_id == current_user.id
        )
    )
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get tasks
    result = await db.execute(
        select(Task)
        .where(Task.assignment_id == assignment_id)
        .order_by(Task.order)
    )
    tasks = result.scalars().all()

    return tasks


@router.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks for current user, optionally filtered by status."""
    query = select(Task).where(Task.user_id == current_user.id)

    if status:
        query = query.where(Task.status == status)

    query = query.order_by(Task.scheduled_date.nullslast(), Task.order)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task (mark complete, update time, reschedule)."""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    if request.status is not None:
        task.status = request.status
        if request.status == "completed":
            task.completed_at = datetime.utcnow()

    if request.completed_at is not None:
        task.completed_at = request.completed_at

    if request.actual_minutes is not None:
        task.actual_minutes = request.actual_minutes

    if request.scheduled_date is not None:
        task.scheduled_date = request.scheduled_date

    await db.commit()
    await db.refresh(task)

    # Update assignment completion percentage
    await update_assignment_progress(task.assignment_id, db)

    return task


async def update_assignment_progress(assignment_id: int, db: AsyncSession):
    """Recalculate assignment completion % based on tasks."""
    result = await db.execute(
        select(Task).where(Task.assignment_id == assignment_id)
    )
    tasks = result.scalars().all()

    if not tasks:
        return

    completed_count = sum(1 for t in tasks if t.status == "completed")
    completion_percentage = (completed_count / len(tasks)) * 100

    await db.execute(
        update(Assignment)
        .where(Assignment.id == assignment_id)
        .values(completion_percentage=completion_percentage)
    )
    await db.commit()


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()

    return {"status": "success", "message": "Task deleted"}
```

### 4. Frontend Implementation

#### API Client: `frontend/src/api/tasks.ts`
```typescript
import { apiClient } from './client';

export interface Task {
  id: number;
  assignment_id: number;
  title: string;
  description?: string;
  order: number;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  completed_at?: string;
  estimated_minutes?: number;
  actual_minutes?: number;
  scheduled_date?: string;
  category?: 'setup' | 'research' | 'implementation' | 'testing' | 'documentation' | 'submission';
  difficulty?: 'easy' | 'medium' | 'hard';
}

export interface GenerateTasksRequest {
  regenerate?: boolean;
  auto_schedule?: boolean;
}

export const tasksApi = {
  generateTasks: async (assignmentId: number, data: GenerateTasksRequest) => {
    const response = await apiClient.post<Task[]>(
      `/assignments/${assignmentId}/generate-tasks`,
      data
    );
    return response.data;
  },

  getTasksForAssignment: async (assignmentId: number) => {
    const response = await apiClient.get<Task[]>(`/assignments/${assignmentId}/tasks`);
    return response.data;
  },

  getAllTasks: async (status?: string) => {
    const response = await apiClient.get<Task[]>('/tasks', {
      params: status ? { status } : {},
    });
    return response.data;
  },

  updateTask: async (taskId: number, data: Partial<Task>) => {
    const response = await apiClient.patch<Task>(`/tasks/${taskId}`, data);
    return response.data;
  },

  deleteTask: async (taskId: number) => {
    const response = await apiClient.delete(`/tasks/${taskId}`);
    return response.data;
  },
};
```

#### Component: `frontend/src/components/TaskList.tsx`
```tsx
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, Circle, Clock, ChevronRight, Loader2 } from 'lucide-react';
import { tasksApi, Task } from '../api/tasks';

interface TaskListProps {
  assignmentId: number;
}

export function TaskList({ assignmentId }: TaskListProps) {
  const queryClient = useQueryClient();

  // Get tasks
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', assignmentId],
    queryFn: () => tasksApi.getTasksForAssignment(assignmentId),
  });

  // Generate tasks mutation
  const generateMutation = useMutation({
    mutationFn: (data: { regenerate: boolean }) =>
      tasksApi.generateTasks(assignmentId, { ...data, auto_schedule: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', assignmentId] });
    },
  });

  // Update task mutation
  const updateMutation = useMutation({
    mutationFn: ({ taskId, data }: { taskId: number; data: Partial<Task> }) =>
      tasksApi.updateTask(taskId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', assignmentId] });
      queryClient.invalidateQueries({ queryKey: ['assignments'] });
    },
  });

  const handleToggleTask = (task: Task) => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    updateMutation.mutate({
      taskId: task.id,
      data: {
        status: newStatus,
        completed_at: newStatus === 'completed' ? new Date().toISOString() : undefined,
      },
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'in_progress':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return <div className="text-center py-4">Loading tasks...</div>;
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-600 mb-4">No task breakdown yet</p>
        <button
          onClick={() => generateMutation.mutate({ regenerate: false })}
          disabled={generateMutation.isPending}
          className="btn-primary"
        >
          {generateMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating Tasks...
            </>
          ) : (
            <>Generate Task Breakdown</>
          )}
        </button>
      </div>
    );
  }

  const completedCount = tasks.filter((t) => t.status === 'completed').length;
  const progressPercent = Math.round((completedCount / tasks.length) * 100);

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Progress: {completedCount}/{tasks.length} tasks
          </span>
          <span className="text-sm font-semibold text-gray-900">{progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Task list */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Task Breakdown</h3>
          <button
            onClick={() => generateMutation.mutate({ regenerate: true })}
            disabled={generateMutation.isPending}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Regenerate
          </button>
        </div>

        <div className="space-y-2">
          {tasks.map((task) => (
            <div
              key={task.id}
              className={`flex items-start gap-3 p-3 rounded-md border transition-colors ${
                task.status === 'completed'
                  ? 'bg-gray-50 border-gray-200'
                  : 'bg-white border-gray-200 hover:border-blue-300'
              }`}
            >
              <button
                onClick={() => handleToggleTask(task)}
                className="mt-0.5 flex-shrink-0"
              >
                {getStatusIcon(task.status)}
              </button>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <h4
                    className={`text-sm font-medium ${
                      task.status === 'completed'
                        ? 'text-gray-500 line-through'
                        : 'text-gray-900'
                    }`}
                  >
                    {task.title}
                  </h4>
                  {task.estimated_minutes && (
                    <span className="text-xs text-gray-500 flex items-center gap-1 flex-shrink-0">
                      <Clock className="w-3 h-3" />
                      {task.estimated_minutes < 60
                        ? `${task.estimated_minutes}m`
                        : `${(task.estimated_minutes / 60).toFixed(1)}h`}
                    </span>
                  )}
                </div>

                {task.description && (
                  <p className="text-xs text-gray-600 mt-1">{task.description}</p>
                )}

                <div className="flex items-center gap-2 mt-2">
                  {task.category && (
                    <span className="badge badge-secondary text-xs">{task.category}</span>
                  )}
                  {task.difficulty && (
                    <span className={`badge text-xs ${getDifficultyColor(task.difficulty)}`}>
                      {task.difficulty}
                    </span>
                  )}
                  {task.completed_at && (
                    <span className="text-xs text-gray-500">
                      Completed {new Date(task.completed_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Total time estimate */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Total estimated time:{' '}
            <span className="font-medium text-gray-900">
              {(
                tasks.reduce((sum, t) => sum + (t.estimated_minutes || 0), 0) / 60
              ).toFixed(1)}{' '}
              hours
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

#### Integrate into Assignment Detail Page
```tsx
// frontend/src/pages/Assignments.tsx
import { TaskList } from '../components/TaskList';

// In the assignment detail view:
<div className="space-y-6">
  {/* Assignment details */}

  {/* Task breakdown */}
  <TaskList assignmentId={assignment.id} />
</div>
```

---

## Implementation Plan

### Phase 7A: Backend Foundation (2-3 days)
1. ✅ Create `Task` model
2. ✅ Add migration for `tasks` table
3. ✅ Update `Assignment` and `User` models with relationships
4. ✅ Create `TaskGenerationService` with AI integration
5. ✅ Create task API endpoints
6. ✅ Test with Postman/API docs

### Phase 7B: Frontend UI (2 days)
1. ✅ Create `TaskList` component
2. ✅ Create tasks API client
3. ✅ Integrate into Assignments page
4. ✅ Add loading/error states
5. ✅ Style with Tailwind

### Phase 7C: Automatic Generation (1 day)
1. ✅ Auto-generate tasks when assignment synced from Canvas/Gradescope
2. ✅ Background job or trigger on assignment creation
3. ✅ User can regenerate if needed

### Phase 7D: Calendar Integration (1-2 days)
1. ✅ Sync scheduled tasks to calendar
2. ✅ Show tasks in Dashboard timeline view
3. ✅ Daily task recommendations

### Phase 7E: Polish & Testing (1 day)
1. ✅ Add task reordering (drag & drop)
2. ✅ Add task notes/comments
3. ✅ Task statistics (avg completion time)
4. ✅ Testing

**Total estimate: 7-9 days**

---

## Success Metrics

- **Task generation accuracy**: 80%+ of generated tasks are useful
- **User engagement**: 60%+ of users interact with task breakdowns
- **Completion tracking**: Users with task breakdowns have 30%+ higher assignment completion rate
- **Time estimation**: AI estimates within 30% of actual time spent

---

## Technical Considerations

### AI Cost Management
- Cache task generations per assignment type
- Rate limit generations (3 per assignment max)
- Use smaller model for simple assignments
- Estimate: $0.02-0.05 per task breakdown

### Performance
- Lazy load tasks (don't fetch until user opens assignment)
- Cache task lists in React Query
- Debounce task status updates

### Edge Cases
- Assignment with no description → Use title + course context
- Very simple assignments (< 1 hour) → Generate 2-3 tasks minimum
- Very complex projects (> 40 hours) → Cap at 12 tasks, group subtasks

### Data Privacy
- Tasks are user-specific
- Don't share task breakdowns between users
- Encrypted storage for assignment descriptions

---

## Future Enhancements (Phase 7+)

- **Smart scheduling**: Use calendar availability to auto-schedule
- **Task dependencies**: Block tasks until dependencies complete
- **Pomodoro timer**: Built-in timer for task work sessions
- **AI task assistant**: "I'm stuck on this task" → Get help/resources
- **Habit tracking**: Track which tasks students struggle with
- **Team tasks**: Share task breakdowns with study groups
- **Mobile app**: Push notifications for scheduled tasks

---

## Questions to Answer

1. **When to auto-generate tasks?**
   - On assignment sync? (Could be expensive)
   - On demand only?
   - Background job after sync?

   **Recommendation**: Generate on-demand when user opens assignment detail

2. **How to handle regeneration?**
   - Keep completed tasks, regenerate remaining?
   - Delete all and start fresh?

   **Recommendation**: Prompt user with option

3. **Task granularity?**
   - How detailed should tasks be?
   - 5-12 tasks seems right for most assignments

   **Recommendation**: Adjust based on estimated hours (1 task per 1-3 hours)

4. **Calendar integration?**
   - Create calendar events for each task?
   - Or just scheduled dates in DB?

   **Recommendation**: Start with DB only, add calendar sync later

---

## Next Steps

Ready to implement Phase 7?

**Option 1**: Start with Phase 7A (Backend foundation) - Build Task model and API
**Option 2**: Create minimal prototype first - Single endpoint + basic UI to validate concept
**Option 3**: Do something else

What would you like to do?
