# 🚀 Supabase Integration Complete

Your MediGuard application is now fully integrated with Supabase. This document explains what's been configured and how to complete the setup.

---

## ✅ What's Already Done

### Backend Changes

1. **Configuration**
   - Added Supabase config variables to `.env.example` with clear instructions
   - Updated `core/config.py` to detect Supabase configuration
   - Added automatic fallback to SQLite when Supabase is not configured

2. **Database Connection**
   - `core/database.py` now supports both:
     - **Supabase Postgres** (via `postgresql+asyncpg://`)
     - **SQLite** (local dev fallback via `sqlite+aiosqlite://`)
   - Optimized for Supabase's pgBouncer pooler (statement_cache_size=0)
   - Connection recycling every 5 minutes for serverless compatibility

3. **Authentication (Three-Tier System)**
   - `core/auth.py` verifies JWTs in this order:
     1. **Supabase JWT** (if configured)
     2. **Clerk JWT** (if configured)
     3. **Local HS256 JWT** (dev fallback)
   - New endpoints in `api/routes/auth.py`:
     - `POST /auth/supabase/register` - Create account via Supabase Auth
     - `POST /auth/supabase/login` - Login via Supabase Auth
     - `POST /auth/supabase/refresh` - Refresh session tokens
     - `GET /auth/supabase/status` - Check Supabase connectivity

4. **File Storage**
   - `core/supabase_client.py` - Supabase SDK wrapper with:
     - `upload_prescription()` - Upload prescription images
     - `upload_report()` - Upload PDF reports
     - `verify_supabase_token()` - Verify auth tokens
   - `services/storage_service.py` - Unified storage interface:
     - Automatically uses Supabase when configured
     - Falls back to local `/tmp` storage for dev

5. **Dependencies**
   - ✅ Installed `supabase==2.4.6`
   - ✅ Installed `asyncpg==0.29.0`
   - Updated `requirements.txt`

---

## 🔧 Setup Instructions

### Step 1: Create a Supabase Project

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **New Project**
3. Choose:
   - Organization (or create one)
   - Project name: `mediguard` (or your choice)
   - Database password (save this!)
   - Region (choose closest to your users)
4. Wait 2-3 minutes for provisioning

### Step 2: Get Your Credentials

#### API Keys

1. Go to **Settings → API** in your Supabase dashboard
2. Copy these values:

```env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Database Connection String

1. Go to **Settings → Database**
2. Scroll to **Connection string**
3. Select **URI** tab
4. Choose **Transaction pooler** (uses port 6543)
5. Copy the connection string and:
   - Replace `[YOUR-PASSWORD]` with your database password
   - Change `postgresql://` to `postgresql+asyncpg://`

Example:
```env
DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Step 3: Create Storage Buckets

1. Go to **Storage** in your Supabase dashboard
2. Click **New bucket**
3. Create two buckets:

#### Bucket 1: `prescriptions`
   - Name: `prescriptions`
   - Public bucket: ✅ (checked)
   - Click **Create bucket**

#### Bucket 2: `reports`
   - Name: `reports`
   - Public bucket: ✅ (checked)
   - Click **Create bucket**

### Step 4: Configure Your `.env` File

Open `backend/.env` and add your credentials:

```env
# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

SUPABASE_STORAGE_BUCKET_PRESCRIPTIONS=prescriptions
SUPABASE_STORAGE_BUCKET_REPORTS=reports

# ── OpenAI (Required for MedAgent) ────────────────────────────────────────────
OPENAI_API_KEY=sk-your-openai-key-here

# ── Auth ──────────────────────────────────────────────────────────────────────
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Step 5: Start Your Backend

```bash
cd backend
python main.py
```

The backend will:
- ✅ Detect Supabase is configured
- ✅ Connect to Supabase Postgres (not SQLite)
- ✅ Auto-create all database tables
- ✅ Start at http://localhost:8000

### Step 6: Test the Integration

#### Check Supabase Status
```bash
curl http://localhost:8000/auth/supabase/status
```

Expected response:
```json
{
  "configured": true,
  "url": "https://xxxxx.supabase.co",
  "status": "connected"
}
```

#### Create a Test Account
```bash
curl -X POST http://localhost:8000/auth/supabase/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "phone": "1234567890"
  }'
```

Expected response:
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "provider": "supabase"
}
```

---

## 🎯 What This Gives You

### 1. **Cloud-Native Database**
- No more SQLite limitations
- Full PostgreSQL power (joins, indexes, full-text search)
- Automatic backups
- Scales to production

### 2. **Secure File Storage**
- Prescription images uploaded to Supabase Storage
- PDF reports uploaded to Supabase Storage
- Public URLs with CDN caching
- No local filesystem dependency

### 3. **Production-Ready Auth**
- Industry-standard JWT authentication
- Built-in user management
- Email verification (configurable)
- Password reset flows
- Multi-factor auth support (future)

### 4. **Flexible Deployment**
- Works locally (SQLite fallback) or cloud (Supabase)
- Easy to deploy to any platform (Vercel, Railway, Render)
- Environment-based configuration
- Zero infrastructure management

---

## 📊 Database Tables

The backend automatically creates these tables on startup:

- `users` - User accounts
- `user_profiles` - Health profiles (age, blood type, allergies)
- `medications` - Current medications
- `symptoms` - Symptom logs
- `appointments` - Doctor appointments
- `reminders` - Medication reminders
- `chat_messages` - MedAgent conversations

---

## 🔒 Security Notes

### Environment Variables
- **Never commit** `.env` to Git (already in `.gitignore`)
- Use different credentials for dev/staging/production
- Rotate service role key regularly

### Storage Bucket Policies
The buckets are set to **public** for simplicity. For production:
1. Consider making them private
2. Generate signed URLs with expiry
3. Implement Row-Level Security (RLS) policies

### Database Connection
- Using **transaction pooler** (port 6543) for serverless compatibility
- Connection limit: 5 concurrent (adjustable in `database.py`)
- Connections recycle every 5 minutes

---

## 🐛 Troubleshooting

### "Supabase is not configured"
- Check `.env` file has all required variables
- Restart the backend after changing `.env`

### "Could not connect to database"
- Verify DATABASE_URL is correct
- Check you used the **transaction pooler** (port 6543)
- Verify password has no special characters that need URL encoding
- Test connection from Supabase dashboard: Settings → Database → Connection info

### "Bucket does not exist"
- Create `prescriptions` and `reports` buckets in Supabase dashboard
- Ensure bucket names match exactly (case-sensitive)

### Storage uploads fail
- Verify buckets are set to **public**
- Check Storage → Configuration → CORS settings allow your domain
- View logs: Storage → Logs

### Tables not created
- Check backend startup logs for errors
- Manually run: `python -c "from core.database import create_tables; import asyncio; asyncio.run(create_tables())"`

---

## 📝 Next Steps

### Optional: Disable SQLite Fallback
Once Supabase is working, you can remove SQLite support:

1. Remove from `requirements.txt`:
   ```
   aiosqlite==0.20.0
   ```

2. Update `core/database.py` to require Supabase:
   ```python
   def _build_engine():
       if not settings.DATABASE_URL or settings.is_sqlite:
           raise RuntimeError("DATABASE_URL must be set to a PostgreSQL connection string")
       # ... rest of code
   ```

### Optional: Add Row-Level Security (RLS)
Supabase supports RLS to restrict data access per user:

```sql
-- Example: Users can only see their own medications
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own medications"
  ON medications FOR SELECT
  USING (auth.uid() = user_id);
```

### Optional: Enable Realtime
For live updates (e.g., chat messages):

```python
from core.supabase_client import get_supabase

# Subscribe to changes
client = get_supabase()
channel = client.channel('chat_updates')
channel.on_postgres_changes(
    'INSERT',
    schema='public',
    table='chat_messages',
    callback=on_new_message
).subscribe()
```

---

## 🎉 You're All Set!

Your MediGuard app now has:
- ✅ Cloud-native PostgreSQL database
- ✅ Supabase Storage for files
- ✅ Production-ready authentication
- ✅ Automatic fallback for local development

Frontend is running at: http://localhost:3000  
Backend API docs: http://localhost:8000/docs

Happy coding! 🚀
