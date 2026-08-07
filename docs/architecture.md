# MediGuard — System Architecture

## Overview

MediGuard is a full-stack AI health management platform. The system is split into three layers:

1. **Frontend** — Next.js 14 app (browser)
2. **Backend** — FastAPI Python service (API + AI + business logic)
3. **Infrastructure** — Supabase PostgreSQL, Qdrant, Redis, Supabase Storage

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser / Mobile                         │
│                     Next.js 14 + Tailwind                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS (REST JSON)
                               │ Bearer JWT
┌──────────────────────────────▼──────────────────────────────────┐
│                        FastAPI Backend                          │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  /auth   │  │ /profile │  │  /meds   │  │  /symptoms    │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  /chat   │  │ /appts   │  │/reminders│  │  /dashboard   │  │
│  └────┬─────┘  └──────────┘  └──────────┘  └───────────────┘  │
│       │                                                         │
│  ┌────▼──────────────────────────────────────────────────────┐  │
│  │                    MedAgent (LangGraph)                   │  │
│  │                                                           │  │
│  │  agent_node ──► tools_node ──► agent_node ──► END        │  │
│  │                                                           │  │
│  │  Tools: get_medication_history  get_symptom_history       │  │
│  │         get_user_profile        recall_from_memory        │  │
│  │         check_drug_interaction                            │  │
│  └────┬──────────────────────────────────────────────────────┘  │
│       │                                                         │
│  ┌────▼─────────────────────────────┐                          │
│  │     Hindsight Memory Engine      │                          │
│  │  QdrantMemory │ InMemoryFallback │                          │
│  └────┬─────────────────────────────┘                          │
│       │                                                         │
└───────┼─────────────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────┐
│                       Infrastructure                            │
│                                                                 │
│  Supabase PostgreSQL    Qdrant (vector DB)    Redis (cache)     │
│  Supabase Storage       (QDRANT_ENABLED=true) (optional)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
mediguard/
├── backend/
│   ├── main.py                    FastAPI app, CORS, lifespan, routers
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── agents/
│   │   ├── medagent.py            LangGraph StateGraph (agent ↔ tools loop)
│   │   └── tools.py               5 async tools, per-request context wiring
│   │
│   ├── memory/
│   │   └── hindsight.py           QdrantMemory + InMemoryFallback, get_memory()
│   │
│   ├── api/
│   │   ├── schemas.py             Pydantic request/response models
│   │   └── routes/
│   │       ├── auth.py            Supabase Auth, Clerk sync, local JWT
│   │       ├── profile.py         Health profile + emergency card
│   │       ├── medications.py     CRUD + OCR scan endpoint
│   │       ├── symptoms.py        Log + list symptoms
│   │       ├── chat.py            MedAgent chat, session management
│   │       ├── appointments.py    CRUD + AI summary
│   │       ├── reminders.py       Create / update reminders
│   │       ├── dashboard.py       Aggregated health stats
│   │       └── reports.py         PDF download
│   │
│   ├── models/
│   │   ├── user.py                User + relationships
│   │   ├── profile.py             UserProfile (medical history)
│   │   ├── medication.py          Medication + DrugInteraction
│   │   ├── symptom.py             Symptom + AI analysis fields
│   │   ├── appointment.py         Appointment + AI summary fields
│   │   ├── reminder.py            Reminder with recurrence
│   │   └── chat.py                ChatSession + ChatMessage
│   │
│   ├── services/
│   │   ├── medication_service.py  CRUD + _run_interaction_check()
│   │   ├── symptom_service.py     create_symptom() + _analyze_symptom()
│   │   ├── appointment_service.py CRUD + generate_appointment_summary()
│   │   ├── ocr_service.py         GPT-4o Vision prescription extraction
│   │   ├── report_service.py      ReportLab PDF generation
│   │   └── storage_service.py     Supabase Storage upload/download
│   │
│   └── core/
│       ├── config.py              Pydantic Settings, auto-detect LLM provider
│       ├── database.py            Async SQLAlchemy engine + session factory
│       ├── auth.py                3-tier JWT: Supabase → Clerk → local HS256
│       ├── redis_client.py        Optional Redis (no-op when URL empty)
│       └── supabase_client.py     Supabase Python client wrapper
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx               Landing page
│   │   ├── layout.tsx             Root layout
│   │   ├── (auth)/                Sign-in / Sign-up (Clerk)
│   │   └── (dashboard)/
│   │       ├── layout.tsx         Sidebar + protected shell
│   │       └── dashboard/
│   │           ├── page.tsx       Health dashboard
│   │           ├── medications/   Medication manager
│   │           ├── symptoms/      Symptom tracker
│   │           ├── chat/          MedAgent chat UI
│   │           ├── appointments/  Appointment manager
│   │           ├── reminders/     Reminder manager
│   │           ├── reports/       PDF download
│   │           ├── emergency/     Emergency card
│   │           └── profile/       Health profile editor
│   │
│   ├── components/
│   │   ├── layout/sidebar.tsx     Navigation sidebar
│   │   └── providers/
│   │       ├── auth-provider.tsx  Auth context (Clerk wrapper)
│   │       └── query-provider.tsx TanStack Query client
│   │
│   └── lib/
│       ├── api.ts                 Axios client, setAuthToken(), all API calls
│       └── utils.ts               Shared utilities
│
└── docker-compose.yml             PostgreSQL + Redis + Qdrant
```

---

## Data Flow: Adding a Medication

```
POST /api/v1/medications
         │
         ▼
  MedicationCreate (Pydantic validation)
         │
         ▼
  create_medication() [medication_service.py]
    ├── INSERT medication → Postgres (flush, get ID)
    ├── _run_interaction_check()
    │     ├── configure_tools(user_id, db, memory)
    │     ├── check_drug_interaction.ainvoke({new_drug})
    │     │     ├── get_medication_history() → SELECT FROM medications
    │     │     └── Groq LLM (pharmacist prompt) → JSON interactions
    │     ├── INSERT drug_interactions → Postgres
    │     └── memory.store(type="event") for HIGH/CRITICAL severity
    ├── memory.store(type="medication")   ← Hindsight write
    └── COMMIT
         │
         ▼
  Response: { medication, interactions[], interaction_count, has_critical }
```

## Data Flow: MedAgent Chat Turn

```
POST /api/v1/chat  { message, session_id? }
         │
         ▼
  Get or create ChatSession
  Load last 20 ChatMessages as history
         │
         ▼
  agent.chat(user_id, message, history, db, memory)
    ├── configure_tools(user_id, db, memory)
    ├── Build LangChain message list from history
    └── graph.ainvoke({messages, user_id})
          │
          ▼
      agent_node (Groq/OpenAI with bound tools)
          │
          ├─ tool_calls present? ──► tools_node
          │                              │
          │    ┌──────────────────────── ▼ ─────────────────────────┐
          │    │  get_medication_history()  → SELECT medications      │
          │    │  get_symptom_history()     → SELECT symptoms         │
          │    │  get_user_profile()        → SELECT user_profiles    │
          │    │  recall_from_memory()      → Qdrant / in-mem search  │
          │    │  check_drug_interaction()  → DB + Groq LLM           │
          │    └─────────────────────────────────────────────────────┘
          │                              │
          └──────────────────────────────┘ (loop back to agent_node)
          │
          ▼
      END — extract last AIMessage.content
         │
         ▼
  memory.store(type="conversation")  ← Hindsight write
  INSERT ChatMessage (user) + ChatMessage (assistant)
  COMMIT
         │
         ▼
  Response: { reply, session_id }
```

---

## Authentication Flow

```
Request with Authorization: Bearer <token>
         │
         ▼
  get_current_user_id() [core/auth.py]
    │
    ├── 1. Try Supabase JWT verification (if SUPABASE_URL configured)
    │        └── verify_supabase_token() → returns user_id (sub claim)
    │
    ├── 2. Try Clerk JWT verification (if CLERK_SECRET_KEY set)
    │        └── Fetch JWKS from api.clerk.dev → decode RS256 JWT
    │
    └── 3. Try local HS256 JWT (dev fallback)
               └── jose.jwt.decode(SECRET_KEY, HS256) → sub claim
```

---

## Memory Architecture

```
get_memory() → singleton HindsightMemory instance
                │
                ├── QDRANT_ENABLED=true  →  QdrantMemory
                │     ├── store()   embed(content) → upsert Qdrant point
                │     ├── recall()  embed(query) → cosine similarity search
                │     └── filter by user_id + optional memory_type
                │
                └── QDRANT_ENABLED=false →  InMemoryFallback
                      ├── store()   append to process-local list
                      └── recall()  keyword overlap scoring

Memory types written:
  "medication"    — on every medication add
  "symptom"       — on every symptom log (includes AI analysis)
  "event"         — on HIGH/CRITICAL drug interactions
  "conversation"  — on every MedAgent chat turn
```

---

## Database Schema (Key Tables)

```
users
  id (PK, UUID), clerk_id (unique), email (unique),
  full_name, phone, avatar_url, is_active, created_at, updated_at

user_profiles
  id (PK), user_id (FK→users), age, gender, weight_kg, height_cm,
  blood_group, medical_conditions (JSON), allergies (JSON),
  current_diseases (JSON), emergency_contact_*, notes

medications
  id (PK), user_id (FK→users), name, generic_name, dosage, frequency,
  route, start_date, end_date, prescribing_doctor, pharmacy, purpose,
  notes, status (enum), reminder_times (JSON), ocr_source,
  prescription_image_url, created_at, updated_at

drug_interactions
  id (PK), user_id (FK→users), medication_a_id (FK→medications),
  medication_b_name, interaction_type, severity (enum),
  description, recommendation, is_acknowledged, detected_at

symptoms
  id (PK), user_id (FK→users), name, severity (enum), severity_score,
  body_location, duration_hours, notes, ai_analysis, possible_causes (JSON),
  related_medications (JSON), logged_at

appointments
  id (PK), user_id (FK→users), doctor_name, specialty, location,
  scheduled_at, status (enum), notes, ai_summary,
  questions_for_doctor (JSON), recent_medication_changes (JSON),
  recent_symptoms (JSON), created_at, updated_at

reminders
  id (PK), user_id (FK→users), medication_id (FK→medications, nullable),
  reminder_type (enum), title, message, scheduled_at, status (enum),
  is_recurring, recurrence_rule, snoozed_until, completed_at, created_at

chat_sessions
  id (PK), user_id (FK→users), title, created_at, updated_at

chat_messages
  id (PK), session_id (FK→chat_sessions), role (enum: user|assistant),
  content, created_at
```
