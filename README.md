# Student Hub

A full-stack web application that helps students manage their academic workload by syncing assignments from Canvas and Gradescope, tracking job opportunities from LinkedIn, and automatically breaking down assignments into actionable tasks using AI.

## Features

### Assignment Management
- **Canvas Integration**: OAuth sync for courses and assignments
- **Gradescope Integration**: Web scraping with SSO support
- **AI Task Breakdown**: Automatically generates 5-8 actionable subtasks for each assignment using Claude AI
- **Calendar View**: Visual timeline of all upcoming assignments

### Job Tracking
- **LinkedIn Scraping**: Automated job opportunity discovery
- **Application Tracking**: Monitor application status and deadlines
- **Smart Filtering**: Find relevant opportunities based on your profile

### Smart Organization
- **Priority-Based Todo Lists**: Tasks ordered by priority and due date
- **Gmail Integration**: Track important academic emails
- **Progress Tracking**: Visual completion metrics and analytics

## Tech Stack

### Backend
- **FastAPI** - Async Python web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Alembic** - Database migrations
- **Playwright** - Web scraping (Gradescope, LinkedIn)
- **Anthropic Claude** - AI task generation (Haiku model)
- **APScheduler** - Background job scheduling

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Styling
- **Vite** - Build tool

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. **Install dependencies**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL (PostgreSQL connection)
# - SECRET_KEY (for JWT tokens)
# - ANTHROPIC_API_KEY (for AI task generation)
# - Canvas API credentials
# - Gmail OAuth credentials
```

3. **Initialize database**:
```bash
# Run migrations
alembic upgrade head

# Initialize admin account (optional)
python init_db.py
```

4. **Start the server**:
```bash
uvicorn app.main:app --reload
# API runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

3. **Start dev server**:
```bash
npm run dev
# App runs at http://localhost:5173
```

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── services/        # Business logic
│   │   └── core/            # Auth, config, dependencies
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # API client functions
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── store/           # State management
│   └── package.json
├── EXERCISES.md             # Learning exercises for developers
├── LICENSE
└── README.md
```

## Key Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Assignments
- `GET /api/v1/assignments` - List assignments
- `POST /api/v1/canvas/sync` - Sync from Canvas
- `POST /api/v1/gradescope/sync` - Sync from Gradescope

### Tasks
- `GET /api/v1/tasks?status=pending` - Get pending tasks
- `POST /api/v1/assignments/{id}/generate-tasks` - Generate AI tasks
- `PATCH /api/v1/tasks/{id}` - Update task
- `POST /api/v1/tasks/{id}/complete` - Mark complete

### Jobs
- `GET /api/v1/jobs` - List job opportunities
- `POST /api/v1/jobs/scrape` - Scrape LinkedIn

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/studenthub

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-fernet-key-here

# AI
ANTHROPIC_API_KEY=your-anthropic-key

# Canvas
CANVAS_API_URL=https://canvas.instructure.com
CANVAS_CLIENT_ID=your-client-id
CANVAS_CLIENT_SECRET=your-client-secret

# Gmail (Optional)
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Deployment

### Backend (Railway)
- Automatically deploys from `main` branch
- Uses `railway.json` configuration
- PostgreSQL database auto-provisioned

### Frontend (Vercel)
- Automatically deploys from `main` branch
- Uses `frontend/vercel.json` configuration
- Environment variables set in Vercel dashboard

## Development

### Running Tests
```bash
# Backend (when tests exist)
cd backend
pytest

# Frontend (when tests exist)
cd frontend
npm test
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Learning

New to the codebase? Check out **EXERCISES.md** for a comprehensive learning guide with 20+ hands-on exercises covering:
- Backend architecture (FastAPI, SQLAlchemy, async/await)
- Frontend patterns (React, TypeScript, TanStack Query)
- Security and production readiness
- Testing and deployment

## License

MIT
