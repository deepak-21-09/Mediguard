# MediGuard — AI-Powered Medication Management Platform

> One AI agent that remembers your entire medication journey, catches dangerous drug interactions, and prepares you for every doctor visit.

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![Tests](https://img.shields.io/badge/e2e%20tests-26%2F26%20passing-brightgreen)](#testing)
[![License](https://img.shields.io/badge/license-MIT-blue)](#license)

---

## What It Does

MediGuard is a full-stack health management platform built around **MedAgent** — a LangGraph-based AI agent with five live database tools and a persistent memory engine ([Hindsight](https://hindsight.vectorize.io/)). Unlike session-only chatbots, MedAgent accumulates context permanently: every medication added, every symptom logged, every drug interaction flagged is stored and semantically retrievable across all future sessions.

**Core capabilities:**
- **Drug interaction detection** — every new medication triggers an AI pharmacist check against the patient's full active list, with severity scoring (low / moderate / high / critical) persisted to the database
- **Symptom analysis** — AI correlates logged symptoms against current medications and flags likely side effects
- **Persistent memory** — Qdrant vector store (with in-memory fallback) makes every health event searchable by meaning, not just keywords
- **Appointment prep** — AI generates a pre-visit summary with symptom timeline, medication changes, and questions to ask the doctor
- **Emergency card** — one-tap view of allergies, blood group, active medications, and emergency contacts
- **PDF health reports** — downloadable full history via ReportLab
- **Prescription OCR** — upload a prescription image; GPT-4o Vision extracts structured medication data

---

## Architecture

```
mediguard/
├── frontend/                  Next.js 14 + Tailwind CSS + Clerk Auth
├── backend/
│   ├── agents/
│   │   ├── medagent.py        LangGraph StateGraph (agent ↔ tools loop)
│   │   └── tools.py           5 async tools wired to live DB queries
│   ├── memory/
│   │   └── hindsight.py       Qdrant vector store + in-memory fallback
│   ├── models/                SQLAlchemy ORM models (PostgreSQL)
│   ├── services/              Business logic + AI calls
│   ├── api/routes/            FastAPI routers
│   └── core/                  Config, DB engine, Auth, Redis
└── docker-compose.yml         Full stack (Postgres + Redis + Qdrant)
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, Tailwind CSS, Radix UI, TanStack Query |
| Backend | FastAPI, Python 3.11, SQLAlchemy (async), asyncpg |
| AI Agent | LangGraph, LangChain, Groq (`llama-3.1-8b-instant`) or OpenAI |
| Memory | Hindsight — Qdrant vector store (cosine similarity recall) |
| Database | Supabase PostgreSQL |
| Cache | Redis (optional — no request path dependency) |
| Auth | Clerk (production) / local HS256 JWT (dev) |
| PDF | ReportLab |
| OCR | GPT-4o Vision (requires `OPENAI_API_KEY`) |
| Deploy | Docker Compose, production-ready CORS + env config |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- A [Supabase](https://supabase.com) project (free tier works)
- A [Groq](https://console.groq.com) API key (free)

### 1. Clone

```bash
git clone https://github.com/deepak-21-09/Mediguard.git
cd Mediguard
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:

```env
# Supabase — get from your project dashboard → Settings → API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql+asyncpg://postgres.yourproject:PASSWORD@aws-0-region.pooler.supabase.com:6543/postgres

# Groq (free tier) — https://console.groq.com
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# JWT secret (any random string for dev)
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# App
ENVIRONMENT=development
DEBUG=true

# Optional
OPENAI_API_KEY=        # enables GPT-4o Vision prescription OCR
CLERK_SECRET_KEY=      # enables Clerk auth
REDIS_URL=             # optional caching
QDRANT_ENABLED=false   # set true + configure host for vector memory
```

Start the backend:

```bash
python main.py
# → http://localhost:8000
# → Swagger UI: http://localhost:8000/docs
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_placeholder
CLERK_SECRET_KEY=sk_test_placeholder
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
# → http://localhost:3000
```

---

## API Reference

Full interactive docs at `http://localhost:8000/docs` once the backend is running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server health + environment info |
| `POST` | `/api/v1/auth/register` | Register / sync user |
| `POST` | `/api/v1/auth/token` | Get local dev JWT |
| `GET/PUT` | `/api/v1/profile` | Read / update health profile |
| `GET` | `/api/v1/profile/emergency-card` | Emergency info card |
| `GET` | `/api/v1/dashboard` | Aggregated health dashboard |
| `GET/POST` | `/api/v1/medications` | List / add medication (triggers interaction check) |
| `PUT/DELETE` | `/api/v1/medications/{id}` | Update / delete medication |
| `POST` | `/api/v1/medications/scan-prescription` | OCR prescription image |
| `GET/POST` | `/api/v1/symptoms` | List / log symptom (triggers AI analysis) |
| `GET/POST` | `/api/v1/appointments` | List / create appointment |
| `POST` | `/api/v1/appointments/{id}/summary` | Generate AI pre-visit summary |
| `GET/POST` | `/api/v1/reminders` | List / create reminder |
| `POST` | `/api/v1/chat` | Chat with MedAgent |
| `GET` | `/api/v1/chat/sessions` | List chat sessions |
| `GET` | `/api/v1/reports/health-report.pdf` | Download PDF report |

---

## Testing

The project ships with a full end-to-end test suite that runs against a live backend and real Supabase PostgreSQL:

```bash
cd backend
# With backend already running on :8000
python e2e_test.py
```

**26 tests covering:**
- Auth (register, JWT)
- Profile (read, update)
- Dashboard
- Medications (CRUD, AI interaction detection)
- Symptoms (log + AI analysis)
- Appointments + reminders
- Emergency card
- MedAgent chat (new session, tool call turn, session list, message history)
- Supabase data verification (raw SQL count checks)

Expected output:
```
  RESULTS: 26/26 passed   0 failed   0 warnings
  🎉 ALL TESTS PASSED — Backend is production-ready!
```

---

## MedAgent & Memory Architecture

MedAgent is a [LangGraph](https://github.com/langchain-ai/langgraph) `StateGraph` with two nodes — `agent` and `tools` — connected by a conditional edge. If the LLM's response contains tool calls, execution routes to the tool executor and loops back. Otherwise it terminates.

The five tools are all async SQLAlchemy queries against the live user database:

| Tool | What it does |
|------|-------------|
| `get_medication_history` | Full medication list, filterable by name |
| `get_symptom_history` | Symptoms from the last N days |
| `get_user_profile` | Age, weight, allergies, conditions |
| `recall_from_memory` | Semantic search over Hindsight memories |
| `check_drug_interaction` | LLM pharmacist check against active meds |

Every health event is written to [Hindsight](https://hindsight.vectorize.io/) with a typed memory category (`medication`, `symptom`, `event`, `conversation`). In production with Qdrant enabled, memories are embedded with `text-embedding-3-small` and retrieved by cosine similarity. Without Qdrant, an in-memory keyword fallback keeps the full pipeline functional for development.

---

## Production Deployment

Set these in `backend/.env` before deploying:

```env
ENVIRONMENT=production
DEBUG=false
# CORS is automatically locked to https://mediguard.app in production mode.
# Override with a comma-separated list for custom domains:
CORS_ORIGINS=https://your-domain.com,https://preview.your-domain.com
```

The `/health` endpoint confirms the active config:

```json
{
  "status": "ok",
  "environment": "production",
  "debug": false,
  "database": "supabase_postgres",
  "cors_origins": ["https://mediguard.app"]
}
```

---

## Clerk Auth (Full Multi-User)

For production multi-user auth:

1. Create a Clerk app at [clerk.com](https://clerk.com)
2. Set `CLERK_SECRET_KEY` in both `backend/.env` and `frontend/.env.local`
3. Set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` in `frontend/.env.local`
4. The backend `core/auth.py` already verifies Clerk JWTs automatically when the key is present

Without Clerk keys the backend falls through to local HS256 JWT — sufficient for development and single-user demos.

---

## License

MIT