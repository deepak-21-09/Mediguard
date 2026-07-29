# 🚀 MediGuard Quick Start Guide

Get MediGuard running locally in 5 minutes, then connect to Supabase for cloud deployment.

---

## ⚡ Quick Local Setup (No Supabase Required)

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- Git installed

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment

The `backend/.env` file already has development defaults. You only need to add your OpenAI API key:

Open `backend/.env` and update:
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

**Get an OpenAI key:** https://platform.openai.com/api-keys

### Step 3: Start the Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend is now running at:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

### Step 4: Install Frontend Dependencies

Open a **new terminal** window:

```bash
cd frontend
npm install
```

### Step 5: Configure Frontend

Open `frontend/.env.local` and verify:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
```

### Step 6: Start the Frontend

```bash
cd frontend
npm run dev
```

You should see:
```
✓ Ready on http://localhost:3000
```

**Frontend is now running at:** http://localhost:3000

---

## 🎯 Test the App

1. **Open your browser:** http://localhost:3000
2. **Create an account** (uses local JWT auth)
3. **Explore features:**
   - Dashboard - Health overview
   - Medications - Track your meds
   - Symptoms - Log daily symptoms
   - Chat - Talk to MedAgent AI
   - Appointments - Manage doctor visits
   - Reports - Generate health reports

---

## 🌟 What's Running

### Local Mode (Current Setup)
- ✅ Backend: FastAPI on http://localhost:8000
- ✅ Database: SQLite (`backend/mediguard.db`)
- ✅ Storage: Local `/tmp` folder
- ✅ Auth: Local JWT tokens
- ✅ Frontend: Next.js on http://localhost:3000

### Database Tables (Auto-Created)
- `users` - User accounts
- `user_profiles` - Health profiles
- `medications` - Medication tracking
- `symptoms` - Symptom logs
- `appointments` - Doctor appointments
- `reminders` - Medication reminders
- `chat_messages` - AI chat history

---

## 🔐 Authentication Options

### Option 1: Local Dev (Current)
- Simple JWT tokens
- No external services needed
- Perfect for development

### Option 2: Supabase Auth
See **SUPABASE_SETUP.md** for full cloud integration.

### Option 3: Clerk Auth
1. Create account at https://clerk.com
2. Get your keys from the dashboard
3. Update `backend/.env`:
   ```env
   CLERK_SECRET_KEY=sk_test_xxxxx
   CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
   ```
4. Update `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
   ```

---

## 🚀 Upgrade to Supabase (Cloud)

When you're ready to move to production:

1. Follow **SUPABASE_SETUP.md** (detailed guide)
2. Quick summary:
   - Create Supabase project
   - Copy credentials to `backend/.env`
   - Create storage buckets
   - Restart backend

Your app will automatically switch from SQLite → Supabase Postgres!

---

## 📊 Project Structure

```
Mediguard/
├── backend/
│   ├── agents/          # MedAgent AI logic
│   │   ├── medagent.py  # Main AI agent
│   │   └── tools.py     # Agent tools (search, analyze)
│   ├── api/
│   │   └── routes/      # API endpoints
│   │       ├── auth.py
│   │       ├── medications.py
│   │       ├── symptoms.py
│   │       ├── chat.py
│   │       └── ...
│   ├── core/
│   │   ├── database.py       # Database connection
│   │   ├── auth.py           # JWT verification
│   │   ├── config.py         # Settings
│   │   └── supabase_client.py # Supabase SDK
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   ├── memory/          # Hindsight memory system
│   ├── .env             # Environment config
│   ├── main.py          # Backend entry point
│   └── requirements.txt # Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/      # Sign in/up pages
│   │   └── (dashboard)/ # Main app pages
│   │       ├── appointments/
│   │       ├── medications/
│   │       ├── symptoms/
│   │       ├── chat/
│   │       └── ...
│   ├── components/      # React components
│   ├── lib/             # Utilities
│   ├── .env.local       # Frontend config
│   └── package.json     # Node dependencies
│
├── docker-compose.yml   # Optional Docker setup
├── QUICKSTART.md        # This file
├── SUPABASE_SETUP.md   # Cloud deployment guide
├── prd.md              # Product requirements
└── srs.md              # Software requirements spec
```

---

## 🛠️ Development Commands

### Backend
```bash
# Start server
cd backend
python main.py

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Check database
sqlite3 mediguard.db
.tables
.schema users
```

### Frontend
```bash
# Start dev server
cd frontend
npm run dev

# Build for production
npm run build

# Install new package
npm install package-name
```

---

## 🔍 API Endpoints

### Authentication
- `POST /auth/supabase/register` - Create account
- `POST /auth/supabase/login` - Login
- `GET /auth/supabase/status` - Check Supabase connection

### Medications
- `GET /medications` - List user's medications
- `POST /medications` - Add medication
- `PUT /medications/{id}` - Update medication
- `DELETE /medications/{id}` - Delete medication
- `POST /medications/{id}/check-interactions` - Check drug interactions

### Symptoms
- `GET /symptoms` - List symptom logs
- `POST /symptoms` - Log new symptom
- `GET /symptoms/analytics` - Get symptom patterns

### Chat (MedAgent)
- `POST /chat` - Send message to AI
- `GET /chat/history` - Get conversation history
- `DELETE /chat` - Clear history

### Appointments
- `GET /appointments` - List appointments
- `POST /appointments` - Create appointment
- `PUT /appointments/{id}` - Update appointment

### Reports
- `POST /reports/generate` - Generate health PDF report

**Full API docs:** http://localhost:8000/docs

---

## 🧪 Testing the AI Agent

### Example Chat Requests

```bash
# Ask about medication interactions
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "I just started taking Aspirin. Any interactions with my current meds?",
    "user_id": "1"
  }'

# Ask about symptoms
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "I have a headache and nausea. What could it be?",
    "user_id": "1"
  }'
```

---

## 💾 Database Management

### View Your Data
```bash
cd backend
sqlite3 mediguard.db

# List all tables
.tables

# View users
SELECT * FROM users;

# View medications
SELECT * FROM medications;

# View chat history
SELECT * FROM chat_messages ORDER BY created_at DESC LIMIT 10;

# Exit
.quit
```

### Reset Database
```bash
cd backend
rm mediguard.db
python main.py  # Will recreate tables
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check for port conflicts
netstat -ano | findstr :8000
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev

# Check Node version
node --version  # Should be 18+
```

### OpenAI API errors
- Verify your API key is correct
- Check you have credits: https://platform.openai.com/usage
- Make sure key starts with `sk-`

### Chat doesn't work
- Check `OPENAI_API_KEY` in `backend/.env`
- View backend logs for errors
- Test API directly: http://localhost:8000/docs

### "Module not found" errors
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 📖 Key Features

### 1. Medication Tracking
- Add medications with dosage, frequency, instructions
- Set reminders for each medication
- Track medication history
- Upload prescription images (OCR coming soon)

### 2. Drug Interaction Checking
- Automatic checks when adding new medications
- Real-time analysis against full medication history
- Severity ratings and recommendations
- Powered by OpenAI GPT-4

### 3. Symptom Logging
- Daily symptom tracking
- Severity scale (1-10)
- Automatic pattern detection
- Correlate symptoms with medication changes

### 4. MedAgent AI Chat
- Natural language health assistant
- Remembers your full medical history (Hindsight memory)
- Answers medication questions
- Provides health guidance (not medical advice)
- Contextual awareness of all your data

### 5. Appointment Management
- Schedule doctor appointments
- Track appointment types (checkup, specialist, etc.)
- Add notes and reminders
- View appointment history

### 6. Health Reports
- Generate comprehensive PDF reports
- Include medications, symptoms, appointments
- Perfect for doctor visits
- Shareable and printable

---

## 🎓 Understanding the Architecture

### MedAgent (AI Brain)
- **Location:** `backend/agents/medagent.py`
- **Framework:** LangChain + LangGraph
- **Model:** OpenAI GPT-4
- **Memory:** Hindsight system (persistent memory)
- **Tools:**
  - Medication search
  - Interaction checking
  - Symptom analysis
  - Appointment lookup

### Hindsight Memory
- **Location:** `backend/memory/hindsight.py`
- **Purpose:** Long-term memory for the AI
- **How it works:**
  - Stores important facts from conversations
  - Uses vector similarity search (Qdrant)
  - Recalls relevant context automatically
  - Never forgets your medical history

### Database Models
- **SQLAlchemy ORM** for type-safe database access
- **Async/await** for high performance
- **Automatic migrations** via Alembic (when needed)

---

## 🌐 Deployment Options

### Option 1: Vercel + Supabase (Recommended)
1. Frontend: Deploy to Vercel (automatic from GitHub)
2. Backend: Deploy to Render/Railway/Fly.io
3. Database: Supabase Postgres
4. Storage: Supabase Storage

### Option 2: Docker
```bash
docker-compose up
```

### Option 3: Traditional VPS
- Install Python 3.10+ and Node.js 18+
- Use systemd service for backend
- Use nginx as reverse proxy
- PM2 for frontend process management

---

## 🔒 Security Best Practices

### For Development
- ✅ Use placeholder API keys
- ✅ Don't commit `.env` files
- ✅ Use SQLite for local testing

### For Production
- 🔐 Use strong secret keys
- 🔐 Enable HTTPS (SSL/TLS)
- 🔐 Set CORS properly
- 🔐 Use Supabase Row-Level Security (RLS)
- 🔐 Rotate API keys regularly
- 🔐 Enable rate limiting
- 🔐 Use environment variables (never hardcode secrets)

---

## 📚 Next Steps

1. ✅ **Get it running locally** (you're here!)
2. 📖 **Read the PRD** (`prd.md`) to understand the vision
3. 📖 **Read the SRS** (`srs.md`) for technical requirements
4. 🌐 **Deploy to Supabase** (see `SUPABASE_SETUP.md`)
5. 🎨 **Customize the UI** (edit `frontend/components/`)
6. 🤖 **Enhance MedAgent** (edit `backend/agents/medagent.py`)
7. 📊 **Add analytics** (integrate Mixpanel/PostHog)
8. 🧪 **Write tests** (pytest for backend, Jest for frontend)

---

## 🆘 Getting Help

### Documentation
- **FastAPI docs:** https://fastapi.tiangolo.com
- **Next.js docs:** https://nextjs.org/docs
- **LangChain docs:** https://python.langchain.com
- **Supabase docs:** https://supabase.com/docs

### Logs
- Backend logs: Watch the terminal running `python main.py`
- Frontend logs: Browser console (F12)
- Database logs: Check `backend/mediguard.db`

### Common Issues
See **Troubleshooting** section above.

---

## 🎉 You're Ready!

Your MediGuard development environment is now set up. The app is running locally with SQLite, and you can upgrade to Supabase anytime by following `SUPABASE_SETUP.md`.

**Local URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Happy building! 🚀
