# CampusOS AI

**The AI Operating System for Higher Education**

CampusOS AI is not a chatbot. It is a coordinated multi-agent platform that serves students, faculty, administrators, admissions teams, career services, and support departments through a single intelligent interface.

## Architecture

- **Backend:** FastAPI (Python) with 12 specialized agents orchestrated by a central router
- **Frontend:** Next.js 15 portal with chat and executive dashboard
- **Database:** PostgreSQL 16 with pgvector for RAG
- **Cache/Queue:** Redis (stub for workflow engine)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend dev without Docker)
- Python 3.11+ (for local backend dev without Docker)

### Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Seed Demo Data

```bash
docker compose exec backend python /scripts/seed_demo_university.py
```

Or locally:

```bash
cd backend
pip install -r requirements.txt
python ../scripts/seed_demo_university.py
```

## Project Structure

```
├── backend/          # FastAPI API + agent orchestrator
├── frontend/         # Next.js web portal
├── docs/             # Architecture, implementation plan, task tracker
├── scripts/          # Seed and utility scripts
├── docker-compose.yml
└── render.yaml       # Render deployment blueprint
```

## Documentation

| Document | Description |
|---|---|
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Step-by-step phased build guide |
| [docs/TASK_TRACKER.md](docs/TASK_TRACKER.md) | Pending and completed tasks |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and data model |
| [docs/AGENTS.md](docs/AGENTS.md) | Agent responsibilities and permissions |

## Agents

| Agent | Status |
|---|---|
| Knowledge | MVP stub with RAG citations |
| Student Success | MVP stub with credit logic |
| Academic Advisor | Stub |
| Timetable | Stub |
| Campus Navigation | Stub |
| Career | Stub |
| Admissions | Stub |
| Admin Assistant | Stub |
| Faculty Intelligence | Stub |
| Student Retention | Stub |
| Research Assistant | Stub |

## API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many credits do I have left?", "user_role": "student"}'
```

## License

Proprietary — CampusOS AI
