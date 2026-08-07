# Deployment Guide

This guide covers production deployment best practices for MediGuard.

## Production Environment

### Required environment variables

Create `backend/.env` with production settings:

```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
OPENAI_API_KEY=sk-your-openai-key

SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql+asyncpg://postgres:<password>@<project>.db.supabase.co:6543/postgres
SUPABASE_STORAGE_BUCKET_PRESCRIPTIONS=prescriptions
SUPABASE_STORAGE_BUCKET_REPORTS=reports

CLERK_SECRET_KEY=
REDIS_URL=
QDRANT_ENABLED=true
QDRANT_URL=https://<qdrant-host>
CORS_ORIGINS=https://your-domain.com,https://preview.your-domain.com
```

### Production notes

- `DEBUG=false` to disable detailed error output.
- `ENVIRONMENT=production` enables production-safe settings.
- Configure `CORS_ORIGINS` with valid domains for your frontend.
- Use a strong, random `SECRET_KEY`.
- Prefer private Supabase buckets in production, and use signed URLs if available.

## Deployment Options

### Docker Compose

The repository includes `docker-compose.yml` for deploying the full stack.

```bash
docker compose up -d
```

If using Docker Compose, ensure the environment values are set in the compose file or in an `.env` file loaded by Compose.

### Cloud Platform

This app can deploy to many platforms such as:

- Vercel (frontend)
- Render
- Railway
- Fly.io
- Cloudflare Pages + separate backend host

For cloud deployment:

1. Deploy `frontend/` as a Next.js app.
2. Deploy `backend/` with Python and FastAPI.
3. Set environment variables in the target platform.
4. Use HTTPS for all traffic.
5. Set `NEXT_PUBLIC_API_URL` to the backend host.

## Supabase Specific Deployment

### Supabase database

- Use `DATABASE_URL` with the transaction pooler port `6543`.
- Confirm `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` are valid.

### Storage buckets

Create Supabase Storage buckets:

- `prescriptions`
- `reports`

### Authentication

Use Clerk or Supabase Auth in production.

- `CLERK_SECRET_KEY` should be set in both backend and frontend if using Clerk.
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` must exist in `frontend/.env.local`.

## Deployment Checklist

- [ ] `backend/requirements.txt` is installed
- [ ] `frontend/package.json` dependencies are installed
- [ ] `backend/.env` has production values
- [ ] `frontend/.env.local` points to production backend
- [ ] Supabase connection is healthy
- [ ] Storage buckets exist and are configured
- [ ] CORS origins are correct
- [ ] `DEBUG=false` and `ENVIRONMENT=production`

## Running in Production

### Backend

```bash
cd backend
python main.py
```

Or use a process manager such as `gunicorn` or `uvicorn`.

### Frontend

```bash
cd frontend
npm run build
npm start
```

### Health check

Open `https://<backend>/health` to verify service availability.

## Security Recommendations

- Never commit `.env` files.
- Rotate Supabase service role keys regularly.
- Use strong passwords and secrets.
- Restrict CORS to trusted domains.
- Monitor backend logs for API and AI errors.
