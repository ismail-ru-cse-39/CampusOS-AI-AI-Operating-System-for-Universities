# CampusOS AI — Agents Reference

Detailed reference for all 12 specialized agents in the CampusOS multi-agent system.

**Related:** [ARCHITECTURE.md](ARCHITECTURE.md) | [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

---

## Agent Overview

| Agent | Module | Status | Primary Users |
|---|---|---|---|
| Knowledge | `agents/knowledge/` | MVP | All |
| Student Success | `agents/student_success/` | MVP | Students |
| Academic Advisor | `agents/academic_advisor/` | Stub | Students |
| Timetable | `agents/timetable/` | Stub | Students |
| Campus Navigation | `agents/campus_navigation/` | Stub | Students |
| Career | `agents/career/` | Stub | Students |
| Admissions | `agents/admissions/` | Stub | Prospects, Admissions |
| Admin Assistant | `agents/admin_assistant/` | Stub | Students, Admin |
| Faculty Intelligence | `agents/faculty_intelligence/` | Stub | Faculty |
| Retention | `agents/retention/` | Stub | Faculty, Admin, Executive |
| Research Assistant | `agents/research_assistant/` | Stub | Faculty, Research Students |

---

## 1. Knowledge Agent

**The university brain.**

### Responsibilities

- Answer questions about policies, regulations, handbooks, forms, and guides
- Provide cited answers referencing official university documents
- Support natural language queries on any university topic

### Example Queries

- "When is registration?"
- "How do I apply for a scholarship?"
- "What are the requirements for graduation?"
- "How do I transfer departments?"

### Tools and Data Access

- RAG service (`services/rag.py`) — document retrieval
- Document catalog (read-only)
- LLM synthesis (Phase 2)

### Permissions

All authenticated users. Public documents only for students; admin can access internal documents.

---

## 2. Student Success Agent

**Academic guidance and degree progress.**

### Responsibilities

- Credit calculation and tracking
- Graduation eligibility assessment
- Degree progress monitoring
- Personalized academic recommendations

### Example Queries

- "How many credits do I have left?"
- "Can I graduate this semester?"
- "Which courses should I take next?"
- "What happens if I fail this module?"

### Tools and Data Access

- Student memory (profile, enrollments, credits)
- Degree requirements engine (Phase 3)
- Academic standing rules

### Permissions

Students (own data), admins (all students).

---

## 3. Academic Advisor Agent

**Course planning and career pathways.**

### Responsibilities

- Degree roadmap creation
- Course and elective recommendations
- Career pathway planning (e.g., AI Engineer path)
- Research opportunity suggestions

### Example Queries

- "I want to become an AI Engineer — what should I take?"
- "Plan my remaining semesters"
- "What electives complement my major?"

### Tools and Data Access

- Course catalog, program requirements
- Career pathway templates (Phase 3)
- Student memory

### Permissions

Students (own planning), faculty (advisees).

---

## 4. Timetable Agent

**Personalized schedule generation.**

### Responsibilities

- Generate conflict-free schedules
- Optimize for preferred times, days, and locations
- Minimize gaps between classes

### Example Queries

- "Create a timetable with no Friday classes"
- "Schedule my courses in the morning"
- "Build a schedule with minimal campus walking"

### Tools and Data Access

- Course schedule data (Phase 4)
- Constraint solver
- Building location data

### Permissions

Students (own schedule).

---

## 5. Campus Navigation Agent

**Campus wayfinding.**

### Responsibilities

- Building and room directions
- Walking time estimation
- Event location assistance

### Example Queries

- "Where is Engineering Building Room 402?"
- "How long to walk from Library to Business School?"

### Tools and Data Access

- Campus building graph (Phase 7)
- Room directory

### Permissions

All authenticated users.

---

## 6. Career Agent

**Education-to-employment bridge.**

### Responsibilities

- Internship and job matching
- Resume guidance
- Career pathway planning
- Industry trend analysis

### Example Queries

- "Find internships for CS students"
- "What jobs match my skills and GPA?"
- "Help me improve my resume"

### Tools and Data Access

- Student profile (degree, skills, GPA, interests)
- Job/internship database (Phase 4)
- Industry trend data

### Permissions

Students (own profile), career services (all students).

---

## 7. Admissions Agent

**24/7 prospective student support.**

### Responsibilities

- Program recommendations
- Admission requirements and tuition info
- Visa guidance for international applicants
- Application assistance

### Example Queries

- "What programs do you offer in engineering?"
- "What are the entry requirements for MSc Data Science?"
- "How do I apply as an international student?"

### Tools and Data Access

- Program catalog, admission requirements
- Tuition and financial aid documents
- Visa policy documents

### Permissions

Public (unauthenticated prospects in Phase 4), admissions staff.

---

## 8. Administrative Assistant Agent

**Workflow execution for university services.**

### Responsibilities

- Transcript requests
- Enrollment verification
- Appointment booking
- Form submissions and status tracking

### Example Queries

- "Request my official transcript"
- "Verify my enrollment for visa purposes"
- "Book an appointment with the registrar"

### Tools and Data Access

- Workflow engine (`services/workflow_engine.py`)
- Student records (own data)
- Appointment scheduling system (Phase 4)

### Permissions

Students (own requests), admin (all workflows).

---

## 9. Faculty Intelligence Agent

**Instructor and department leader support.**

### Responsibilities

- Identify at-risk students
- Analyze attendance and engagement
- Generate course performance reports
- Recommend interventions

### Example Queries

- "Which students in CS401 are at risk?"
- "Show attendance trends for my course"
- "Generate a performance report for this semester"

### Tools and Data Access

- Course rosters and grade data
- Attendance records (Phase 5)
- Retention risk scores

### Permissions

Faculty (own courses), department heads (department), executive (all).

---

## 10. Student Retention Agent

**Predictive dropout prevention.**

### Responsibilities

- Predict student risk from multiple signals
- Generate early warning alerts
- Recommend interventions before dropout

### Risk Signals

- Low attendance
- Poor performance
- Missed assignments
- Financial risk indicators
- Engagement decline

### Example Queries

- "Which students are at highest dropout risk?"
- "Show retention trends for Engineering"
- "What interventions are recommended for at-risk freshmen?"

### Tools and Data Access

- Retention scoring model (Phase 5)
- Historical retention data
- Intervention playbook

### Permissions

Faculty, admin, executive. Not accessible to students.

---

## 11. Research Assistant Agent

**Research activity support.**

### Responsibilities

- Literature discovery
- Research proposal support
- Grant opportunity matching
- Citation assistance

### Example Queries

- "Find recent papers on transformer architectures"
- "What grants are available for AI research?"
- "Help me format citations for my thesis"

### Tools and Data Access

- Academic paper APIs (Phase 5)
- Grant database
- Citation formatting tools

### Permissions

Faculty, research students, postgraduates.

---

## Orchestrator

**Not an agent — the routing layer.**

Located at `backend/app/agents/orchestrator.py`.

1. Receives user message with role and memory context
2. Scores all agents via `can_handle()`
3. Routes to highest-scoring agent (fallback: Knowledge Agent)
4. Returns structured `AgentResult` with citations

Phase 0 uses keyword scoring. Phase 2+ will add LLM-based intent classification.

---

## Adding a New Agent

1. Create module under `backend/app/agents/<name>/agent.py`
2. Extend `Agent` base class with `name`, `description`, `keywords`
3. Implement `can_handle()` and `run()`
4. Register in `backend/app/agents/registry.py`
5. Document in this file and update [TASK_TRACKER.md](TASK_TRACKER.md)
