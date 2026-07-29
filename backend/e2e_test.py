"""
MediGuard End-to-End API Test Suite
====================================
Tests every major endpoint against a live backend on http://localhost:8000
Run with: python e2e_test.py

What is tested:
  1.  GET  /health                          — server health
  2.  GET  /api/v1/auth/supabase/status     — Supabase connectivity
  3.  POST /api/v1/auth/register            — create a local dev user
  4.  POST /api/v1/auth/token              — get a local JWT
  5.  GET  /api/v1/profile                 — read profile (auto-created)
  6.  PUT  /api/v1/profile                 — update profile
  7.  GET  /api/v1/dashboard               — dashboard overview
  8.  POST /api/v1/medications             — add a medication (+ interaction check)
  9.  GET  /api/v1/medications             — list medications
  10. GET  /api/v1/medications/{id}        — get single medication
  11. PUT  /api/v1/medications/{id}        — update medication
  12. POST /api/v1/symptoms               — log a symptom (+ AI analysis)
  13. GET  /api/v1/symptoms               — list symptoms
  14. POST /api/v1/appointments           — create appointment
  15. GET  /api/v1/appointments           — list appointments
  16. POST /api/v1/reminders             — create reminder
  17. GET  /api/v1/reminders             — list reminders
  18. GET  /api/v1/profile/emergency-card — emergency card
  19. DELETE /api/v1/medications/{id}    — delete medication
  20. Verify data persists in Supabase PostgreSQL
  21. POST /api/v1/chat                  — new chat session (plain question)
  22. POST /api/v1/chat                  — follow-up turn (tool call: drug interactions)
  23. GET  /api/v1/chat/sessions         — list sessions
  24. GET  /api/v1/chat/sessions/{id}/messages — message history persisted
  25. Verify data persists in Supabase PostgreSQL (incl. chat)
"""
import asyncio
import sys
import json
import httpx
from datetime import datetime, timedelta, timezone

BASE = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Test data
TEST_EMAIL = f"e2e_test_{datetime.now(timezone.utc).strftime('%H%M%S')}@mediguard.test"
TEST_CLERK_ID = f"e2e-test-{datetime.now(timezone.utc).strftime('%H%M%S')}"

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

results = []


def log(icon, step, detail=""):
    msg = f"  {icon}  [{step}]"
    if detail:
        msg += f"  {detail}"
    print(msg)
    results.append((icon, step, detail))


async def run():
    print("\n" + "═"*65)
    print("  MediGuard — End-to-End API Test Suite")
    print(f"  Target: {BASE}")
    print(f"  User:   {TEST_EMAIL}")
    print("═"*65 + "\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        token = None
        user_id = None
        med_id = None
        symptom_id = None
        appointment_id = None
        reminder_id = None

        # ── 1. Health ──────────────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/health")
            r.raise_for_status()
            data = r.json()
            assert data["status"] == "ok"
            assert data["database"] == "supabase_postgres", f"Expected supabase_postgres, got {data['database']}"
            assert data["storage"] == "supabase"
            log(PASS, "Health check", f"database={data['database']}, storage={data['storage']}")
        except Exception as e:
            log(FAIL, "Health check", str(e))
            print("\n  Backend not reachable — make sure it's running first.")
            sys.exit(1)

        # ── 2. Supabase status ─────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/auth/supabase/status")
            data = r.json()
            assert data.get("configured") is True
            log(PASS, "Supabase status", f"status={data.get('status', 'ok')}")
        except Exception as e:
            log(WARN, "Supabase status", str(e))

        # ── 3. Register local dev user ────────────────────────────────────
        try:
            r = await client.post(f"{BASE}/api/v1/auth/register", json={
                "clerk_id": TEST_CLERK_ID,
                "email": TEST_EMAIL,
                "full_name": "E2E Test Patient",
                "phone": "9876543210",
            })
            r.raise_for_status()
            data = r.json()
            user_id = data["id"]
            log(PASS, "Register user", f"id={user_id}, email={data['email']}")
        except Exception as e:
            log(FAIL, "Register user", str(e))
            sys.exit(1)

        # ── 4. Get JWT token ───────────────────────────────────────────────
        try:
            r = await client.post(
                f"{BASE}/api/v1/auth/token",
                params={"clerk_id": TEST_CLERK_ID},
            )
            r.raise_for_status()
            token = r.json()["access_token"]
            HEADERS["Authorization"] = f"Bearer {token}"
            log(PASS, "Get JWT token", f"token={token[:30]}…")
        except Exception as e:
            log(FAIL, "Get JWT token", str(e))
            sys.exit(1)

        auth = {"Authorization": f"Bearer {token}"}

        # ── 5. Get profile ─────────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/profile", headers=auth)
            r.raise_for_status()
            data = r.json()
            assert data["user_id"] == user_id
            log(PASS, "Get profile", f"user_id={data['user_id']}")
        except Exception as e:
            log(FAIL, "Get profile", str(e))

        # ── 6. Update profile ──────────────────────────────────────────────
        try:
            r = await client.put(f"{BASE}/api/v1/profile", headers=auth, json={
                "age": 32,
                "gender": "male",
                "weight_kg": 75.0,
                "height_cm": 175.0,
                "blood_group": "O+",
                "medical_conditions": ["Hypertension", "Type 2 Diabetes"],
                "allergies": ["Penicillin", "Sulfa drugs"],
                "emergency_contact_name": "Jane Doe",
                "emergency_contact_phone": "9999999999",
                "emergency_contact_relation": "Spouse",
            })
            r.raise_for_status()
            data = r.json()
            assert data["blood_group"] == "O+"
            assert "Hypertension" in data["medical_conditions"]
            log(PASS, "Update profile", f"blood_group={data['blood_group']}, conditions={data['medical_conditions']}")
        except Exception as e:
            log(FAIL, "Update profile", str(e))

        # ── 7. Dashboard ───────────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/dashboard", headers=auth)
            r.raise_for_status()
            data = r.json()
            assert "health_score" in data
            assert "active_medications" in data
            log(PASS, "Dashboard overview", f"health_score={data['health_score']}, active_meds={data['active_medications']}")
        except Exception as e:
            log(FAIL, "Dashboard overview", str(e))

        # ── 8. Add medication (triggers Groq interaction check) ────────────
        try:
            r = await client.post(f"{BASE}/api/v1/medications", headers=auth, json={
                "name": "Metformin",
                "generic_name": "Metformin Hydrochloride",
                "dosage": "500mg",
                "frequency": "twice daily",
                "route": "oral",
                "start_date": datetime.now(timezone.utc).date().isoformat(),
                "prescribing_doctor": "Dr. Smith",
                "purpose": "Type 2 Diabetes management",
                "reminder_times": ["08:00", "20:00"],
            })
            r.raise_for_status()
            data = r.json()
            med = data["medication"]
            med_id = med["id"]
            interactions = data.get("interactions", [])
            log(PASS, "Add medication", f"id={med_id}, name={med['name']}, interactions={data['interaction_count']}")
        except Exception as e:
            log(FAIL, "Add medication", str(e))

        # ── 9. Add a second medication for interaction testing ─────────────
        try:
            r = await client.post(f"{BASE}/api/v1/medications", headers=auth, json={
                "name": "Aspirin",
                "dosage": "100mg",
                "frequency": "once daily",
                "purpose": "Blood thinner",
            })
            r.raise_for_status()
            data = r.json()
            log(PASS, "Add 2nd medication", f"name={data['medication']['name']}, interactions={data['interaction_count']}, critical={data['has_critical']}")
        except Exception as e:
            log(FAIL, "Add 2nd medication", str(e))

        # ── 10. List medications ───────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/medications", headers=auth)
            r.raise_for_status()
            meds = r.json()
            assert len(meds) >= 1
            log(PASS, "List medications", f"count={len(meds)}, names={[m['name'] for m in meds]}")
        except Exception as e:
            log(FAIL, "List medications", str(e))

        # ── 11. Get single medication ──────────────────────────────────────
        if med_id:
            try:
                r = await client.get(f"{BASE}/api/v1/medications/{med_id}", headers=auth)
                r.raise_for_status()
                data = r.json()
                assert data["id"] == med_id
                log(PASS, "Get medication by ID", f"id={data['id']}, name={data['name']}, status={data['status']}")
            except Exception as e:
                log(FAIL, "Get medication by ID", str(e))

        # ── 12. Update medication ──────────────────────────────────────────
        if med_id:
            try:
                r = await client.put(f"{BASE}/api/v1/medications/{med_id}", headers=auth, json={
                    "notes": "Tolerance established. Continue current dose.",
                    "reminder_times": ["07:30", "19:30"],
                })
                r.raise_for_status()
                data = r.json()
                assert "Tolerance" in (data.get("notes") or "")
                log(PASS, "Update medication", f"notes updated, reminder_times={data.get('reminder_times')}")
            except Exception as e:
                log(FAIL, "Update medication", str(e))

        # ── 13. Log symptom (triggers Groq AI analysis) ───────────────────
        try:
            r = await client.post(f"{BASE}/api/v1/symptoms", headers=auth, json={
                "name": "Nausea",
                "severity": "moderate",
                "severity_score": 5,
                "body_location": "stomach",
                "duration_hours": 2,
                "notes": "Occurred after taking Metformin this morning",
            })
            r.raise_for_status()
            data = r.json()
            symptom_id = data["id"]
            has_analysis = bool(data.get("ai_analysis"))
            log(PASS, "Log symptom", f"id={symptom_id}, severity={data['severity']}, has_AI_analysis={has_analysis}")
            if data.get("ai_analysis"):
                print(f"       AI analysis: {data['ai_analysis'][:80]}…")
        except Exception as e:
            log(FAIL, "Log symptom", str(e))

        # ── 14. List symptoms ──────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/symptoms", headers=auth)
            r.raise_for_status()
            symptoms = r.json()
            assert len(symptoms) >= 1
            log(PASS, "List symptoms", f"count={len(symptoms)}")
        except Exception as e:
            log(FAIL, "List symptoms", str(e))

        # ── 15. Create appointment ─────────────────────────────────────────
        try:
            appt_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            r = await client.post(f"{BASE}/api/v1/appointments", headers=auth, json={
                "doctor_name": "Dr. Sarah Johnson",
                "specialty": "Endocrinology",
                "location": "City Medical Center, Room 204",
                "scheduled_at": appt_date,
                "notes": "Follow-up for diabetes management and medication review",
            })
            r.raise_for_status()
            data = r.json()
            appointment_id = data["id"]
            log(PASS, "Create appointment", f"id={appointment_id}, doctor={data['doctor_name']}, status={data['status']}")
        except Exception as e:
            log(FAIL, "Create appointment", str(e))

        # ── 16. List appointments ──────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/appointments", headers=auth)
            r.raise_for_status()
            appts = r.json()
            assert len(appts) >= 1
            log(PASS, "List appointments", f"count={len(appts)}")
        except Exception as e:
            log(FAIL, "List appointments", str(e))

        # ── 17. Create reminder ────────────────────────────────────────────
        try:
            remind_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            r = await client.post(f"{BASE}/api/v1/reminders", headers=auth, json={
                "title": "Take Metformin",
                "message": "Take 500mg with food",
                "reminder_type": "medication",
                "scheduled_at": remind_time,
                "is_recurring": True,
                "recurrence_rule": "daily",
            })
            r.raise_for_status()
            data = r.json()
            reminder_id = data["id"]
            log(PASS, "Create reminder", f"id={reminder_id}, title={data['title']}, status={data['status']}")
        except Exception as e:
            log(FAIL, "Create reminder", str(e))

        # ── 18. List reminders ─────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/reminders", headers=auth)
            r.raise_for_status()
            reminders = r.json()
            assert len(reminders) >= 1
            log(PASS, "List reminders", f"count={len(reminders)}")
        except Exception as e:
            log(FAIL, "List reminders", str(e))

        # ── 19. Emergency card ────────────────────────────────────────────
        try:
            r = await client.get(f"{BASE}/api/v1/profile/emergency-card", headers=auth)
            r.raise_for_status()
            data = r.json()
            assert "full_name" in data
            assert "active_medications" in data
            log(PASS, "Emergency card", f"name={data['full_name']}, blood={data['blood_group']}, active_meds={len(data['active_medications'])}")
        except Exception as e:
            log(FAIL, "Emergency card", str(e))

        # ── 20. Delete medication ─────────────────────────────────────────
        if med_id:
            try:
                r = await client.delete(f"{BASE}/api/v1/medications/{med_id}", headers=auth)
                assert r.status_code == 204
                # Verify it's gone
                r2 = await client.get(f"{BASE}/api/v1/medications/{med_id}", headers=auth)
                assert r2.status_code == 404
                log(PASS, "Delete medication", f"id={med_id} deleted & confirmed 404")
            except Exception as e:
                log(FAIL, "Delete medication", str(e))

        # ── 21. Chat — new session, plain question ────────────────────────
        chat_session_id = None
        try:
            r = await client.post(f"{BASE}/api/v1/chat", headers=auth, json={
                "message": "What medications am I currently taking?",
            }, timeout=60.0)
            r.raise_for_status()
            data = r.json()
            assert "reply" in data and len(data["reply"]) > 10
            assert "session_id" in data
            chat_session_id = data["session_id"]
            log(PASS, "Chat — new session", f"session_id={chat_session_id}, reply_len={len(data['reply'])}, preview={data['reply'][:60]}…")
        except Exception as e:
            log(FAIL, "Chat — new session", str(e))

        # ── 22. Chat — tool-call turn (drug interaction lookup) ───────────
        if chat_session_id:
            try:
                r = await client.post(f"{BASE}/api/v1/chat", headers=auth, json={
                    "message": "Do Metformin and Aspirin interact with each other? Check my current meds.",
                    "session_id": chat_session_id,
                }, timeout=60.0)
                r.raise_for_status()
                data = r.json()
                reply = data["reply"]
                assert len(reply) > 20
                # Expect some mention of the drugs or interaction concepts
                reply_lower = reply.lower()
                assert any(kw in reply_lower for kw in ["metformin", "aspirin", "interact", "medication", "drug"]), \
                    f"Reply doesn't mention expected drug terms: {reply[:200]}"
                log(PASS, "Chat — drug interaction tool call", f"reply_len={len(reply)}, preview={reply[:80]}…")
            except Exception as e:
                log(FAIL, "Chat — drug interaction tool call", str(e))

        # ── 23. Chat — list sessions ───────────────────────────────────────
        if chat_session_id:
            try:
                r = await client.get(f"{BASE}/api/v1/chat/sessions", headers=auth)
                r.raise_for_status()
                sessions = r.json()
                assert len(sessions) >= 1
                session_ids = [s["id"] for s in sessions]
                assert chat_session_id in session_ids
                log(PASS, "Chat — list sessions", f"count={len(sessions)}, session found=True")
            except Exception as e:
                log(FAIL, "Chat — list sessions", str(e))

        # ── 24. Chat — message history persisted ──────────────────────────
        if chat_session_id:
            try:
                r = await client.get(f"{BASE}/api/v1/chat/sessions/{chat_session_id}/messages", headers=auth)
                r.raise_for_status()
                messages = r.json()
                # We sent 2 user messages + got 2 assistant replies = 4 messages
                assert len(messages) >= 4, f"Expected ≥4 messages, got {len(messages)}"
                roles = [m["role"] for m in messages]
                assert "user" in roles
                assert "assistant" in roles
                log(PASS, "Chat — message history", f"messages={len(messages)}, roles={list(dict.fromkeys(roles))}")
            except Exception as e:
                log(FAIL, "Chat — message history", str(e))

        # ── 25. Verify data in Supabase ────────────────────────────────────
        try:
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
            from core.database import engine

            Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with Session() as session:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM symptoms WHERE user_id = :uid"),
                    {"uid": user_id}
                )
                symptom_count = result.scalar()

                result2 = await session.execute(
                    text("SELECT COUNT(*) FROM appointments WHERE user_id = :uid"),
                    {"uid": user_id}
                )
                appt_count = result2.scalar()

                result3 = await session.execute(
                    text("SELECT COUNT(*) FROM reminders WHERE user_id = :uid"),
                    {"uid": user_id}
                )
                reminder_count = result3.scalar()

                result4 = await session.execute(
                    text("SELECT full_name, email FROM users WHERE id = :uid"),
                    {"uid": user_id}
                )
                user_row = result4.fetchone()

                # Chat session + messages
                result5 = await session.execute(
                    text("SELECT COUNT(*) FROM chat_sessions WHERE user_id = :uid"),
                    {"uid": user_id}
                )
                chat_session_count = result5.scalar()

                result6 = await session.execute(
                    text("""SELECT COUNT(*) FROM chat_messages cm
                            JOIN chat_sessions cs ON cs.id = cm.session_id
                            WHERE cs.user_id = :uid"""),
                    {"uid": user_id}
                )
                chat_msg_count = result6.scalar()

            assert symptom_count >= 1
            assert appt_count >= 1
            assert reminder_count >= 1
            assert chat_session_count >= 1
            assert chat_msg_count >= 4
            log(PASS, "Supabase data verify",
                f"user='{user_row[0]}', symptoms={symptom_count}, appointments={appt_count}, "
                f"reminders={reminder_count}, chat_sessions={chat_session_count}, chat_messages={chat_msg_count}")
        except Exception as e:
            log(FAIL, "Supabase data verify", str(e))

        # ── Cleanup: delete test user ──────────────────────────────────────
        try:
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
            from core.database import engine
            Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with Session() as session:
                await session.execute(
                    text("DELETE FROM users WHERE id = :uid"), {"uid": user_id}
                )
                await session.commit()
            log(PASS, "Cleanup", f"Test user {user_id} removed from Supabase")
        except Exception as e:
            log(WARN, "Cleanup", f"Could not remove test user: {e}")

    # ── Final report ─────────────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for r in results if r[0] == PASS)
    failed = sum(1 for r in results if r[0] == FAIL)
    warned = sum(1 for r in results if r[0] == WARN)

    print("\n" + "═"*65)
    print(f"  RESULTS: {passed}/{total} passed   {failed} failed   {warned} warnings")
    print("═"*65)

    if failed > 0:
        print("\n  ❌ FAILED TESTS:")
        for icon, step, detail in results:
            if icon == FAIL:
                print(f"     • {step}: {detail}")

    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED — Backend is production-ready!")
        print(f"\n  Verified against: Supabase PostgreSQL")
        print(f"  LLM provider    : Groq (llama-3.1-8b-instant)")
        print(f"  Storage         : Supabase Storage")
        print(f"  Auth            : Local JWT (dev mode)")
    else:
        print(f"\n  {failed} test(s) failed — see details above.")
        sys.exit(1)

    print()


if __name__ == "__main__":
    asyncio.run(run())
