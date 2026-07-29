"""Quick debug — hit the failing endpoints and print full error details."""
import asyncio
import httpx

BASE = "http://localhost:8000"

async def run():
    async with httpx.AsyncClient(timeout=15) as c:
        # Setup: register + token
        r = await c.post(f"{BASE}/api/v1/auth/register", json={
            "clerk_id": "dbg-err-01", "email": "dbgerr@test.co", "full_name": "DbgUser"
        })
        uid = r.json()["id"]
        r2 = await c.post(f"{BASE}/api/v1/auth/token", params={"clerk_id": "dbg-err-01"})
        tok = r2.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}

        # Add a med first so PUT has a real ID
        r3 = await c.post(f"{BASE}/api/v1/medications", headers=h, json={
            "name": "TestMed", "dosage": "100mg", "frequency": "once daily"
        })
        med_id = r3.json()["medication"]["id"]
        print(f"Created med: {med_id}")

        # Test PUT medication
        r4 = await c.put(f"{BASE}/api/v1/medications/{med_id}", headers=h, json={
            "notes": "updated note", "reminder_times": ["08:00"]
        })
        print(f"\nPUT /medications/{med_id}: {r4.status_code}")
        print(r4.text[:500])

        # Test POST symptom
        r5 = await c.post(f"{BASE}/api/v1/symptoms", headers=h, json={
            "name": "Headache", "severity": "mild", "severity_score": 3
        })
        print(f"\nPOST /symptoms: {r5.status_code}")
        print(r5.text[:500])

        # Cleanup
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        from core.database import engine
        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with Session() as s:
            await s.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": uid})
            await s.commit()
        print(f"\nCleaned up user {uid}")

asyncio.run(run())
