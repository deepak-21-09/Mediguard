# MediGuard — AI-Powered Medication Management Platform

> One AI agent that remembers your entire medication journey, catches dangerous interactions, and prepares you for every doctor visit.

---

## Architecture

```
mediguard/
├── frontend/           Next.js 14 + Tailwind CSS + Clerk Auth
├── backend/            FastAPI (Python) + LangGraph + Hindsight Memory
│   ├── agents/         MedAgent (LangGraph + GPT-4o)
│   ├── memory/         Hindsight Memory (Qdrant vector store)
│   ├── models/         SQLAlchemy models (PostgreSQL)
│   ├── services/       Business logic
│   ├── api/routes/     REST API endpoints
│   └── core/           Config, DB, Auth, Redis
└── docker-compose.yml  Full stack (Postgres + Redis + Qdrant)
```

---

## Quick Start

### 1. Prerequisites
- Docker + Docker Compose
- Node.js 20+
- Python 3.11+

### 2. Clone & configure

```bash
# Backend
cp backend/.env.example backend/.env
# Fill in: OPENAI_API_KEY, CLERK_SECRET_KEY

# Frontend
cp frontend/.env.local.example frontend/.env.local
# Fill in: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY
```

### 3. Start infrastructure

```bash
docker-compose up postgres redis qdrant -d
```

### 4. Start backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

---

## API Documentation

Once backend is running: http://localhost:8000/docs (Swagger UI)

### Key endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register/sync Clerk user |
| GET | `/api/v1/dashboard` | Health dashboard |
| GET/POST | `/api/v1/medications` | List / add medication |
| POST | `/api/v1/medications/scan-prescription` | OCR prescription upload |
| GET/POST | `/api/v1/symptoms` | List / log symptoms |
| POST | `/api/v1/chat` | Chat with MedAgent |
| GET | `/api/v1/profile/emergency-card` | Emergency card |
| POST | `/api/v1/appointments/{id}/summary` | AI appointment summary |
| GET | `/api/v1/reports/health-report.pdf` | Download PDF report |

---

## Features Implemented

### Backend
- [x] User auth (Clerk JWT + local JWT fallback)
- [x] User profile with medical history
- [x] Complete medication CRUD
- [x] AI drug interaction detection (GPT-4o) on every add
- [x] Symptom logging with AI analysis
- [x] Hindsight Memory (Qdrant vector store — persistent across sessions)
- [x] MedAgent (LangGraph + GPT-4o with tools)
- [x] Prescription OCR (GPT-4o Vision)
- [x] PDF health report (ReportLab)
- [x] Appointment management + AI pre-visit summary
- [x] Emergency card
- [x] Reminder system
- [x] Health dashboard with health score

### Frontend
- [x] Landing page
- [x] Clerk authentication
- [x] Protected dashboard layout
- [x] Health dashboard
- [x] Medications page (add/scan/delete + interaction warnings)
- [x] Symptom tracker
- [x] MedAgent chat UI
- [x] Appointments + AI summary
- [x] Emergency card
- [x] Health reports (PDF download)
- [x] Reminder management
- [x] Profile editor

---

## Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql+asyncpg://mediguard:mediguard_secret@localhost:5432/mediguard_db
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333
OPENAI_API_KEY=sk-...
CLERK_SECRET_KEY=sk_test_...
SECRET_KEY=your-local-jwt-secret
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, Clerk, TanStack Query |
| Backend | FastAPI, Python 3.11 |
| AI Agent | LangGraph, GPT-4o, OpenAI |
| Memory | Qdrant (vector DB) — Hindsight layer |
| Database | PostgreSQL (SQLAlchemy async) |
| Cache | Redis |
| Auth | Clerk |
| PDF | ReportLab |
| OCR | GPT-4o Vision |
| Deploy | Docker Compose, AWS-ready |
