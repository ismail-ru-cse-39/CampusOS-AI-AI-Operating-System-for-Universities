# CampusOS AI — Implementation Plan

Step-by-step build guide from scaffold to full platform. Each phase lists objectives, key files, acceptance criteria, and dependencies.

**Related:** [TASK_TRACKER.md](TASK_TRACKER.md) | [ARCHITECTURE.md](ARCHITECTURE.md) | [AGENTS.md](AGENTS.md)

---

## Phase 0: Repo Setup and Local Dev

**Status:** Complete (this scaffold)

### Objectives

- Monorepo with FastAPI backend, Next.js frontend, PostgreSQL + pgvector, Redis
- 12 agent modules registered with orchestrator
- Knowledge and Student Success agents with working stubs
- Docker Compose local dev environment
- Render deployment blueprint

### Key Files

| File | Purpose |
|---|---|
| `docker-compose.yml` | Local Postgres, Redis, backend, frontend |
| `backend/app/main.py` | FastAPI entry point |
| `backend/app/agents/orchestrator.py` | Intent routing |
| `frontend/src/app/chat/page.tsx` | Chat UI |
| `scripts/seed_demo_university.py` | Demo data |

### Steps

1. Clone repo and copy `.env.example` to `.env`
2. Run `docker compose up --build`
3. Seed demo data: `docker compose exec backend python /app/../scripts/seed_demo_university.py`
4. Open http://localhost:3000/chat and test queries
5. Verify API docs at http://localhost:8000/docs

### Acceptance Criteria

- [x] Health endpoint returns 12 registered agents
- [x] Chat routes to `student_success` for credit questions
- [x] Chat routes to `knowledge` for policy questions
- [x] Frontend displays agent name and citations

### Dependencies

None.

---

## Phase 1: Auth, RBAC, and Audit Logging

**Status:** Mostly complete — RBAC on agents/routes (T-013), auth/audit/Alembic done; SSO (T-011) and frontend session (T-016) blocked on IdP

### Objectives

- University SSO integration (OIDC/SAML)
- JWT session management with role claims
- Permission-aware API and agent responses
- Audit log for all data access (FERPA/GDPR)

### Steps

1. **Configure SSO provider**
   - Add OIDC client config to `backend/app/core/config.py`
   - Create `backend/app/api/routes/auth.py` with login/callback/logout

2. **Implement auth middleware**
   - Create `backend/app/core/deps.py` with `get_current_user` dependency
   - Protect `/api/v1/chat`, `/students`, `/documents` routes

3. **Wire RBAC enforcement**
   - Extend `backend/app/core/rbac.py` with agent-level permissions
   - Agents check `has_permission()` before returning sensitive data

4. **Audit logging service**
   - Create `backend/app/services/audit.py`
   - Log every chat request, document access, and profile view to `audit_logs` table

5. **Alembic migrations**
   - Initialize Alembic in `backend/app/db/migrations/`
   - Generate initial migration from existing models

6. **Frontend auth flow**
   - Add login page and session provider in `frontend/src/`
   - Pass JWT to API calls in `frontend/src/lib/api.ts`

### Acceptance Criteria

- [ ] Users authenticate via SSO and receive role-scoped JWT (blocked — use `/auth/dev-token` for dev)
- [x] RBAC enforced on agents and protected routes
- [x] Students cannot access retention/executive agents
- [x] Audit log entries on chat and profile views

### Dependencies

Phase 0.

---

## Phase 2: Knowledge Agent (Full RAG)

**Status:** Mostly complete — ingestion, upload API, hybrid search done; real OpenAI wiring (T-017/T-020) blocked on API key

### Objectives

- Document ingestion pipeline (PDF, HTML, DOCX)
- pgvector embeddings and semantic search
- LLM-powered answer synthesis with mandatory citations
- Admin document upload API

### Steps

1. **LLM integration**
   - Wire `backend/app/services/llm.py` to OpenAI embeddings + completions
   - Add retry logic and token budgeting

2. **Document ingestion**
   - Create `backend/app/services/ingestion.py` — chunk, embed, store in `document_chunks`
   - Add `POST /api/v1/documents/upload` route

3. **Vector search**
   - Replace keyword search in `backend/app/services/rag.py` with pgvector cosine similarity
   - Enable `CREATE EXTENSION vector` on Postgres startup

4. **Knowledge Agent upgrade**
   - Update `backend/app/agents/knowledge/agent.py` to use LLM for answer synthesis
   - Always attach citation list from retrieved chunks

5. **Admin upload UI**
   - Add document management page in frontend

### Acceptance Criteria

- [x] Upload documents via API (txt/md/html; PDF placeholder)
- [x] Answers include document title, URL, and excerpt citations
- [x] Semantic search structure with mock embeddings (real embeds need `OPENAI_API_KEY`)

### Dependencies

Phase 1 (auth for document upload).

---

## Phase 3: Student Success and Academic Advisor Agents

**Status:** Complete (T-023 through T-028)

### Objectives

- Real student profile lookup from database
- Credit calculation and graduation eligibility logic
- Degree roadmap and elective recommendations
- Personalized student memory from DB

### Steps

1. **Student memory service**
   - Create `backend/app/services/memory.py` loading profile + enrollments from DB
   - Replace `DEMO_STUDENT_MEMORY` in orchestrator

2. **Degree requirements engine**
   - Create `backend/app/services/degree.py` with program requirement rules
   - Add `program_requirements` table and model

3. **Student Success Agent upgrade**
   - Integrate degree engine for graduation eligibility
   - Handle edge cases: failed modules, academic standing, prerequisites

4. **Academic Advisor Agent**
   - Implement roadmap generation in `backend/app/agents/academic_advisor/agent.py`
   - Career pathway templates (e.g., AI Engineer path)

5. **Student dashboard UI**
   - Show credits, progress bar, upcoming deadlines in frontend

### Acceptance Criteria

- [x] "Can I graduate this semester?" uses degree engine + student memory
- [x] "I want to become an AI Engineer" returns course + elective plan
- [x] Memory loaded from DB with demo fallback

### Dependencies

Phase 1, Phase 2 (for policy cross-references).

---

## Phase 4: Workflow Engine and Service Agents

**Status:** Mostly complete — workflow engine and service agents done; Redis worker (T-030) stub only

### Objectives

- Workflow engine for administrative task execution
- Admin Assistant, Timetable, Admissions, Career, Campus Navigation agents
- Background job processing with Redis queue

### Steps

1. **Workflow engine**
   - Implement state machine in `backend/app/services/workflow_engine.py`
   - Define workflows: transcript_request, enrollment_verification, appointment_booking

2. **Background workers**
   - Add Celery or Render background worker service
   - Wire Redis queue in `docker-compose.yml`

3. **Admin Assistant Agent**
   - Execute workflows instead of giving instructions
   - Return workflow ID and status tracking URL

4. **Timetable Agent**
   - Constraint solver for schedule optimization
   - Integrate course schedule data model

5. **Admissions, Career, Campus Navigation agents**
   - Implement domain-specific tools and data sources

### Acceptance Criteria

- [x] "Request my transcript" starts a workflow and returns tracking ID
- [x] Timetable generates conflict-free schedule with preferences
- [x] Admissions agent answers prospect questions with demo catalog

### Dependencies

Phase 1, Phase 3.

---

## Phase 5: Faculty Intelligence, Retention, and Predictive Analytics

**Status:** Complete (T-036 through T-040)

### Objectives

- At-risk student identification
- Early warning alerts
- Executive dashboard with real metrics
- Weekly AI-generated executive reports

### Steps

1. **Risk scoring model**
   - Create `backend/app/services/retention.py` with rule-based + ML scoring
   - Inputs: attendance, grades, assignment completion, engagement

2. **Faculty Intelligence Agent**
   - Course analytics, roster insights, intervention recommendations

3. **Retention Agent**
   - Early warning alerts with recommended interventions

4. **Executive dashboard**
   - Replace stub metrics in `frontend/src/app/dashboard/page.tsx`
   - Add charts: retention trends, enrollment forecast, department performance

5. **Report generation**
   - Scheduled weekly report via cron job or Render cron

### Acceptance Criteria

- [x] Faculty sees at-risk students via retention scoring
- [x] Executive dashboard fetches live metrics from analytics API
- [x] Weekly report stub at `/api/v1/analytics/weekly-report` (email blocked on SMTP)

### Dependencies

Phase 3, Phase 4.

---

## Phase 6: Communication Hub

**Status:** Partial — notification service with stub adapters (T-041); channel integrations blocked

### Objectives

- Proactive notifications across channels
- Email, SMS, WhatsApp, Teams, Slack integrations
- Assignment reminders, registration alerts, career fair invitations

### Steps

1. **Notification service**
   - Create `backend/app/services/notifications.py` with channel adapters

2. **Event triggers**
   - Deadline approaching, grade posted, at-risk alert, registration opening

3. **Channel integrations**
   - SMTP for email, Twilio for SMS, webhook adapters for Teams/Slack

4. **User notification preferences**
   - Per-user channel opt-in stored in DB

### Acceptance Criteria

- [ ] Students receive assignment reminders via preferred channel (blocked — SMTP/Twilio)
- [x] At-risk alerts dispatched via in-app notification stub

### Dependencies

Phase 5.

---

## Phase 7: University Knowledge Graph

**Status:** Partial — Postgres adjacency graph + query API (T-046/T-047); Neo4j deployment blocked

### Objectives

- Digital twin of university entities and relationships
- Cross-entity reasoning (student → courses → faculty → buildings)

### Steps

1. **Graph database setup**
   - Deploy Neo4j or use PostgreSQL with graph extensions
   - Implement `backend/app/services/knowledge_graph.py`

2. **Entity sync pipeline**
   - Sync students, courses, departments, buildings, policies from Postgres

3. **Graph-powered agent tools**
   - Agents query graph for relationship-aware answers

### Acceptance Criteria

- [x] Graph query API returns program/course/faculty relationships
- [x] Navigation agent uses building graph for walking routes

### Dependencies

Phase 3, Phase 4.

---

## Phase 8: Voice, Multilingual, and Enterprise Deployment

**Status:** Mostly complete — i18n, voice stub, multi-tenant branding done; CI/CD (T-051) blocked

### Objectives

- Voice input/output
- Multilingual support (EN, AR, ZH, ES, FR, HI, BN)
- Multi-campus and white-label deployment
- Private cloud options

### Steps

1. **i18n framework**
   - Add translation layer for agent responses
   - Language detection on input

2. **Voice interface**
   - Speech-to-text and text-to-speech integration
   - Mobile app or web voice UI

3. **Multi-tenant enterprise**
   - University-level branding, config, and data isolation
   - White-label frontend theming

4. **Production hardening**
   - CI/CD pipeline, load testing, monitoring, backup strategy

### Acceptance Criteria

- [x] i18n structure with 7 languages (EN full, others stub entries)
- [x] Voice input stub in chat UI
- [x] Multi-tenant branding via `/api/v1/tenants/{slug}`

### Dependencies

All prior phases.

---

## How to Use This Plan

1. Check [TASK_TRACKER.md](TASK_TRACKER.md) for current task status
2. Pick the next `Pending` task in the current phase
3. Mark it `In Progress`, implement, then mark `Done`
4. Verify acceptance criteria before moving to the next phase
