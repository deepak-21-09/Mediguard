# Setup Guide

This guide explains how to set up MediGuard locally, configure environment variables, and connect to Supabase for cloud deployment.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git (optional)
- OpenAI API key for AI features
- Supabase project (optional, but required for production)

## Local Development Setup

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Backend Environment

Create `backend/.env` with the following values:

```env
# Supabase (optional for local dev)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=sqlite+aiosqlite:///./mediguard.db

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# Auth and app settings
SECRET_KEY=change-me-in-development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=development
DEBUG=true

# Optional services
CLERK_SECRET_KEY=
REDIS_URL=
QDRANT_ENABLED=false
QDRANT_URL=
```

> Use `sqlite+aiosqlite:///./mediguard.db` for local development. The backend will auto-create database tables.

### 3. Start the Backend

```bash
cd backend
python main.py
```

The backend should start on `http://localhost:8000`.

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Frontend Environment

Create `frontend/.env.local` with at least the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### 6. Start the Frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` to view the app.

## Supabase Cloud Setup

The app supports Supabase PostgreSQL and Supabase Storage in production.

### 1. Create a Supabase Project

- Visit https://supabase.com and create a new project.
- Save your database password.

### 2. Get Supabase Credentials

From the Supabase dashboard:

- **SUPABASE_URL**
- **SUPABASE_ANON_KEY**
- **SUPABASE_SERVICE_ROLE_KEY**
- **DATABASE_URL** using the transaction pooler port `6543`

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<password>@<project>.db.supabase.co:6543/postgres
```

### 3. Create Storage Buckets

Create two public buckets in Storage:

- `prescriptions`
- `reports`

### 4. Update `backend/.env`

```env
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql+asyncpg://postgres:<password>@<project>.db.supabase.co:6543/postgres
SUPABASE_STORAGE_BUCKET_PRESCRIPTIONS=prescriptions
SUPABASE_STORAGE_BUCKET_REPORTS=reports
OPENAI_API_KEY=sk-your-openai-key
SECRET_KEY=your-production-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=production
DEBUG=false
```

### 5. Restart the Backend

Stop the backend and run:

```bash
cd backend
python main.py
```

### 6. Verify Supabase Connection

Open `http://localhost:8000/auth/supabase/status` and confirm the status is connected.

## Troubleshooting

### Backend fails to start

- Ensure Python 3.11+ is installed.
- Activate the virtual environment.
- Confirm `requirements.txt` packages are installed.
- Make sure `backend/.env` exists and contains `OPENAI_API_KEY`.

### Frontend build issues

- Run `npm install` in `frontend/`.
- If port `3000` is taken, use `npm run dev -- -p 3001`.
- Confirm `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`.

### Supabase issues

- Check `DATABASE_URL` is using `postgresql+asyncpg://`.
- Ensure the port is `6543` for the transaction pooler.
- Confirm the `SUPABASE_SERVICE_ROLE_KEY` is valid.

## Next Steps

- Visit `http://localhost:8000/docs` for interactive backend API docs.
- Visit `http://localhost:3000` to use the frontend.
- Read `docs/api-reference.md` to understand available endpoints.
- Read `docs/architecture.md` for system design and AI details.
