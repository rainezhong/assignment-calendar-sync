# Assignment Calendar Sync - Backend API

FastAPI backend with PostgreSQL database for the Assignment Calendar Sync application.

## Features

- **Authentication**: JWT-based auth with refresh tokens
- **Assignment Intelligence**: AI-powered complexity analysis using Bloom's Taxonomy
- **Performance Analytics**: Time series tracking of academic health metrics
- **Predictive Assistant**: Risk prediction and workload optimization
- **RESTful API**: Clean, documented endpoints with OpenAPI/Swagger

## Tech Stack

- **FastAPI**: Modern async Python web framework
- **SQLAlchemy 2.0**: Async ORM with PostgreSQL
- **Alembic**: Database migrations
- **Pydantic**: Data validation and settings
- **JWT**: Secure token-based authentication
- **OpenAI/Anthropic**: AI-powered analysis (Phase 4 agents)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (for caching)

### Installation

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Create database**:
   ```bash
   createdb assignment_sync
   ```

5. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

### Running the Server

**Development** (with auto-reload):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── assignments.py       # Assignment CRUD
│   │       ├── intelligence.py      # AI analysis (Phase 4)
│   │       ├── analytics.py         # Performance tracking (Phase 4)
│   │       └── predictions.py       # Risk & optimization (Phase 4)
│   ├── core/
│   │   ├── config.py               # Settings and configuration
│   │   ├── security.py             # JWT and password hashing
│   │   └── deps.py                 # FastAPI dependencies
│   ├── db/
│   │   └── session.py              # Database session management
│   ├── models/
│   │   ├── user.py                 # User model
│   │   ├── assignment.py           # Assignment model
│   │   └── analytics.py            # Analytics models
│   ├── services/                    # Business logic (TODO)
│   │   ├── intelligence.py         # Wraps assignment_intelligence.py
│   │   ├── analytics.py            # Wraps performance_analytics.py
│   │   └── predictions.py          # Wraps predictive_assistant.py
│   └── main.py                     # FastAPI application
├── alembic/                        # Database migrations
├── tests/                          # Test suite
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment template
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login and get tokens
- `GET /api/v1/auth/me` - Get current user

### Assignments
- `GET /api/v1/assignments` - List assignments
- `POST /api/v1/assignments` - Create assignment
- `GET /api/v1/assignments/{id}` - Get assignment
- `PATCH /api/v1/assignments/{id}` - Update assignment
- `DELETE /api/v1/assignments/{id}` - Delete assignment

### Intelligence (Phase 4)
- `POST /api/v1/intelligence/{id}/analyze` - Run AI analysis
- `GET /api/v1/intelligence/{id}/skills` - Get required skills
- `GET /api/v1/intelligence/{id}/resources` - Get recommendations

### Analytics (Phase 4)
- `GET /api/v1/analytics/health` - Get health score
- `GET /api/v1/analytics/trends` - Get performance trends
- `GET /api/v1/analytics/summary` - Get full analytics

### Predictions (Phase 4)
- `GET /api/v1/predictions/risk/{id}` - Assess deadline risk
- `POST /api/v1/predictions/optimize-workload` - Optimize schedule
- `GET /api/v1/predictions/suggestions` - Get AI suggestions

## Database Schema

### Users Table
- id, email, hashed_password, full_name
- is_active, is_verified, is_premium
- google_id, google_access_token (OAuth)
- created_at, updated_at, last_login

### Assignments Table
- id, user_id, title, description
- course_name, assignment_type, due_date
- complexity_score, blooms_level, estimated_hours
- required_skills (JSON), recommended_resources (JSON)
- is_completed, completion_percentage, actual_hours_spent

### Performance Metrics Table
- id, user_id, metric_type, metric_value
- course_name, category, metadata (JSON)
- recorded_at (timestamped)

### Predictions Table
- id, user_id, assignment_id
- prediction_type, predicted_value, confidence_score
- risk_level, risk_factors (JSON), suggestions (JSON)
- actual_value, was_accurate (for learning)

## Environment Variables

See `.env.example` for full list. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude
- `GOOGLE_CLIENT_ID`: Google OAuth credentials
- `REDIS_URL`: Redis connection for caching

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## Deployment

### Railway (Recommended for MVP)

1. Push to GitHub
2. Connect Railway to your repo
3. Add PostgreSQL plugin
4. Set environment variables
5. Deploy!

### Manual Deployment

Use gunicorn with uvicorn workers:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Next Steps

1. **Integrate Phase 4 Agents**: Connect the existing Python agents
   - Copy `python/agents/` code into `app/services/`
   - Update imports and add async wrappers

2. **Add Background Tasks**: Use Celery for async AI processing

3. **Implement Caching**: Add Redis caching for expensive operations

4. **Add Rate Limiting**: Protect endpoints with rate limits

5. **Set up Monitoring**: Add logging, metrics, and error tracking

## License

MIT - See LICENSE file
