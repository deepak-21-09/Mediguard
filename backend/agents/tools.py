"""
MedAgent tools — each tool gives the agent access to the user's health data.
"""
from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

# These are set per-request in the agent runner
_user_id: str = ""
_db_session = None
_memory = None


def configure_tools(user_id: str, db_session, memory):
    global _user_id, _db_session, _memory
    _user_id = user_id
    _db_session = db_session
    _memory = memory


@tool
async def get_medication_history(query: str = "") -> str:
    """
    Retrieve the user's full medication history.
    Optionally pass a query to filter by name or purpose.
    """
    from sqlalchemy import select
    from models.medication import Medication

    stmt = select(Medication).where(Medication.user_id == _user_id)
    result = await _db_session.execute(stmt)
    meds = result.scalars().all()

    if query:
        meds = [m for m in meds if query.lower() in m.name.lower()]

    return json.dumps([
        {
            "name": m.name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "status": m.status,
            "start_date": str(m.start_date) if m.start_date else None,
            "end_date": str(m.end_date) if m.end_date else None,
            "purpose": m.purpose,
        }
        for m in meds
    ])


@tool
async def get_symptom_history(days: int = 30) -> str:
    """
    Retrieve symptoms logged by the user in the last N days.
    """
    from sqlalchemy import select
    from models.symptom import Symptom
    from datetime import datetime, timedelta

    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Symptom)
        .where(Symptom.user_id == _user_id, Symptom.logged_at >= since)
        .order_by(Symptom.logged_at.desc())
    )
    result = await _db_session.execute(stmt)
    symptoms = result.scalars().all()

    return json.dumps([
        {
            "name": s.name,
            "severity": s.severity,
            "logged_at": s.logged_at.isoformat(),
            "notes": s.notes,
            "related_medications": s.related_medications,
        }
        for s in symptoms
    ])


@tool
async def get_user_profile() -> str:
    """
    Get the user's health profile: age, weight, allergies, medical conditions.
    """
    from sqlalchemy import select
    from models.profile import UserProfile

    stmt = select(UserProfile).where(UserProfile.user_id == _user_id)
    result = await _db_session.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        return json.dumps({"error": "No profile found"})

    return json.dumps({
        "age": profile.age,
        "gender": profile.gender,
        "weight_kg": profile.weight_kg,
        "blood_group": profile.blood_group,
        "medical_conditions": profile.medical_conditions,
        "allergies": profile.allergies,
        "current_diseases": profile.current_diseases,
    })


@tool
async def recall_from_memory(query: str) -> str:
    """
    Search the persistent Hindsight memory for relevant past information.
    Use this to answer questions about older events, patterns, or history.
    """
    memories = await _memory.recall(user_id=_user_id, query=query, top_k=8)
    if not memories:
        return "No relevant memories found."
    return json.dumps([
        {"type": m["memory_type"], "content": m["content"], "when": m["timestamp"]}
        for m in memories
    ])


@tool
async def check_drug_interaction(new_drug: str) -> str:
    """
    Check if a new drug interacts with the user's current medications.
    Returns interaction warnings with severity levels.
    """
    from core.config import settings
    import json

    # Get current meds
    med_history = await get_medication_history.ainvoke({"query": ""})
    meds_data = json.loads(med_history)
    active_meds = [m["name"] for m in meds_data if m.get("status") == "active"]

    if not active_meds:
        return json.dumps({"message": "No active medications to check against."})

    prompt = f"""You are a clinical pharmacist. Check interactions between "{new_drug}" and these medications: {active_meds}.
Return a JSON object with key "interactions" containing an array, each item with:
- medication_b: the existing drug name
- interaction_type: "drug-drug", "drug-food", or "allergy"
- severity: "low", "moderate", "high", or "critical"
- description: brief clinical description
- recommendation: what the patient should do

If no interactions, return {{"interactions": []}}."""

    try:
        provider = settings.effective_llm_provider
        if provider == "groq":
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            response = await client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
        else:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"interactions": [], "error": str(e)})


MEDAGENT_TOOLS = [
    get_medication_history,
    get_symptom_history,
    get_user_profile,
    recall_from_memory,
    check_drug_interaction,
]
