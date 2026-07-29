# ✅ MediGuard Getting Started Checklist

Follow this checklist to get your MediGuard app running!

---

## 📋 Pre-Flight Checklist

### System Requirements
- [ ] Python 3.10 or higher installed
  - Check: `python --version`
- [ ] Node.js 18 or higher installed
  - Check: `node --version`
- [ ] Git installed (optional, for version control)
  - Check: `git --version`

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Backend Setup
- [ ] Open terminal and navigate to backend folder
  ```bash
  cd backend
  ```

- [ ] Install Python dependencies
  ```bash
  pip install -r requirements.txt
  ```
  Expected: ~2-3 minutes to install all packages

- [ ] Get an OpenAI API key
  - [ ] Visit https://platform.openai.com/api-keys
  - [ ] Create new key (or use existing)
  - [ ] Copy the key (starts with `sk-`)

- [ ] Configure environment
  - [ ] Open `backend/.env` in a text editor
  - [ ] Find the line: `OPENAI_API_KEY=sk-placeholder-add-your-key-here`
  - [ ] Replace with your actual key: `OPENAI_API_KEY=sk-your-actual-key`
  - [ ] Save the file

- [ ] Start the backend server
  ```bash
  python main.py
  ```
  Expected output:
  ```
  INFO:     Started server process
  INFO:     Uvicorn running on http://0.0.0.0:8000
  ```

- [ ] Verify backend is running
  - [ ] Open browser to: http://localhost:8000/docs
  - [ ] You should see the API documentation page

---

### Step 2: Frontend Setup
- [ ] Open a **NEW terminal window** (keep backend running!)

- [ ] Navigate to frontend folder
  ```bash
  cd frontend
  ```

- [ ] Install Node dependencies
  ```bash
  npm install
  ```
  Expected: ~2-3 minutes to install all packages

- [ ] Start the frontend server
  ```bash
  npm run dev
  ```
  Expected output:
  ```
  ✓ Ready on http://localhost:3000
  ```

- [ ] Verify frontend is running
  - [ ] Open browser to: http://localhost:3000
  - [ ] You should see the MediGuard landing page

---

### Step 3: Test the App
- [ ] Open http://localhost:3000 in your browser

- [ ] Create a test account
  - [ ] Click "Sign Up" or "Get Started"
  - [ ] Fill in test credentials (local auth)
  - [ ] You should be redirected to the dashboard

- [ ] Test the dashboard
  - [ ] Navigate to different pages (Medications, Symptoms, Chat)
  - [ ] Try adding a medication
  - [ ] Try sending a message to the AI chat

---

## ✅ Success Criteria

You should have:
- ✅ Backend running at http://localhost:8000
- ✅ Frontend running at http://localhost:3000
- ✅ API docs visible at http://localhost:8000/docs
- ✅ Landing page loads without errors
- ✅ Can create an account and access dashboard

---

## 🌟 Optional: Supabase Cloud Integration

Want to deploy to the cloud? Follow this checklist:

### Supabase Setup
- [ ] Create a Supabase account at https://supabase.com

- [ ] Create a new project
  - [ ] Choose a project name (e.g., "mediguard")
  - [ ] Set a strong database password (SAVE THIS!)
  - [ ] Select a region close to you
  - [ ] Wait 2-3 minutes for provisioning

- [ ] Get your API credentials
  - [ ] Go to: Settings → API
  - [ ] Copy: `SUPABASE_URL`
  - [ ] Copy: `SUPABASE_ANON_KEY`
  - [ ] Copy: `SUPABASE_SERVICE_ROLE_KEY`

- [ ] Get your database connection string
  - [ ] Go to: Settings → Database
  - [ ] Select: Connection string → URI
  - [ ] Choose: **Transaction pooler** (port 6543)
  - [ ] Copy the connection string
  - [ ] Replace `[YOUR-PASSWORD]` with your database password
  - [ ] Change `postgresql://` to `postgresql+asyncpg://`

- [ ] Create storage buckets
  - [ ] Go to: Storage
  - [ ] Create bucket: `prescriptions` (make it public)
  - [ ] Create bucket: `reports` (make it public)

- [ ] Update your `.env` file
  - [ ] Open `backend/.env`
  - [ ] Update these variables:
    ```env
    SUPABASE_URL=https://xxxxx.supabase.co
    SUPABASE_ANON_KEY=eyJhbGciOiJIUz...
    SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUz...
    DATABASE_URL=postgresql+asyncpg://postgres.xxxxx:[PASSWORD]@...
    ```
  - [ ] Save the file

- [ ] Restart the backend
  - [ ] Stop the backend (Ctrl+C)
  - [ ] Start it again: `python main.py`
  - [ ] Look for: "Using PostgreSQL" in the logs (not SQLite)

- [ ] Test Supabase connection
  - [ ] Open: http://localhost:8000/auth/supabase/status
  - [ ] Should see: `{"configured": true, "status": "connected"}`

- [ ] Done! Your app is now using Supabase! 🎉

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "No module named 'fastapi'"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "Port 8000 already in use"**
- Find and kill the process using port 8000
- Or change the port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`

**Error: "OPENAI_API_KEY not set"**
- Check `backend/.env` has your OpenAI key
- Make sure there are no quotes around the key
- Make sure there are no spaces around the `=`

---

### Frontend won't start

**Error: "Cannot find module 'next'"**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Error: "Port 3000 already in use"**
- Kill the process using port 3000
- Or run: `npm run dev -- -p 3001` (use port 3001 instead)

---

### Chat doesn't respond

**Check backend logs for errors:**
- Look at the terminal running `python main.py`
- Look for OpenAI API errors

**Common issues:**
- OpenAI API key is invalid
- OpenAI account has no credits
- Backend isn't running
- Network/firewall blocking OpenAI API

---

### Database errors

**"No such table: users"**
- The database tables weren't created
- Restart the backend, it will auto-create them
- Check for errors in the logs

**Supabase connection fails**
- Verify your DATABASE_URL is correct
- Check you're using the **transaction pooler** (port 6543)
- Verify your password is correct
- Check you changed `postgresql://` to `postgresql+asyncpg://`

---

## 📚 What to Read Next

### Just want to get it running?
→ You're done! Start using the app.

### Want to understand the architecture?
→ Read `STATUS.md` for a full technical overview

### Ready to deploy to the cloud?
→ Read `SUPABASE_SETUP.md` for detailed Supabase instructions

### Need help with the API?
→ Open http://localhost:8000/docs for interactive API documentation

### Want to understand the product vision?
→ Read `prd.md` (Product Requirements Document)

### Need technical requirements?
→ Read `srs.md` (Software Requirements Specification)

---

## 🎯 Quick Tips

### Development Workflow
1. Keep both terminals open (backend + frontend)
2. Backend changes require restart (Ctrl+C, then `python main.py`)
3. Frontend hot-reloads automatically (just save files)
4. Check backend terminal for API errors
5. Check browser console (F12) for frontend errors

### API Testing
- Use http://localhost:8000/docs for interactive API testing
- Use Postman/Insomnia for complex requests
- Check `Authorization: Bearer <token>` header for protected endpoints

### Database Inspection
```bash
# View SQLite database (local mode)
cd backend
sqlite3 mediguard.db
.tables
SELECT * FROM users;
.quit
```

### Log Locations
- Backend logs: Terminal running `python main.py`
- Frontend logs: Browser console (F12 → Console tab)
- Database file: `backend/mediguard.db` (local mode)

---

## 🎉 You're All Set!

MediGuard is now running on your machine!

### What you have:
- ✅ Full-stack health management app
- ✅ AI-powered health assistant (MedAgent)
- ✅ Medication tracking with interaction checking
- ✅ Symptom logging and pattern detection
- ✅ Appointment management
- ✅ Health report generation

### Your app is accessible at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Next steps:
1. Create an account at http://localhost:3000
2. Add some medications
3. Log some symptoms
4. Chat with the AI assistant
5. Generate your first health report

### Need help?
- Check the troubleshooting section above
- Review the documentation in `QUICKSTART.md`
- Check the API docs at http://localhost:8000/docs

**Happy coding! 🚀**
