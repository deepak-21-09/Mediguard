"""
Symptom service — log symptoms and run AI pattern analysis via MedAgent.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.symptom import Symptom
from models.medication import Medication, MedicationStatus
from memory.hindsight import HindsightMemory
from core.config import settings


async def list_symptoms(
    db: AsyncSession, user_id: str, days: int = 90
) -> list[Symptom]:
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Symptom)
        .where(Symptom.user_id == user_id, Symptom.logged_at >= since)
        .order_by(Symptom.logged_at.desc())
    )
    return result.scalars().all()


async def create_symptom(
    db: AsyncSession,
    user_id: str,
    data: dict,
    memory: HindsightMemory,
) -> Symptom:
    symptom = Symptom(user_id=user_id, **data)

    # AI analysis
    analysis = await _analyze_symptom(db, user_id, symptom)
    symptom.ai_analysis = analysis.get("analysis", "")
    symptom.possible_causes = analysis.get("possible_causes", [])
    symptom.related_medications = analysis.get("related_medications", [])

    db.add(symptom)

    # Store in Hindsight memory
    logged_at_str = (symptom.logged_at or datetime.utcnow()).isoformat()
    await memory.store(
        user_id=user_id,
        memory_type="symptom",
        content=(
            f"Symptom logged: {symptom.name}, severity: {symptom.severity}. "
            f"Notes: {symptom.notes or 'none'}. "
            f"AI analysis: {symptom.ai_analysis}"
        ),
        metadata={
            "symptom_id": str(symptom.id) if symptom.id else "pending",
            "severity": symptom.severity,
            "logged_at": logged_at_str,
        },
    )

    await db.commit()
    await db.refresh(symptom)
    return symptom


async def _analyze_symptom(db: AsyncSession, user_id: str, symptom: Symptom) -> dict:
    """Analyze symptom against current medications using available LLM (Groq or OpenAI)."""
    # Get active medications
    result = await db.execute(
        select(Medication).where(
            Medication.user_id == user_id,
            Medication.status == MedicationStatus.ACTIVE,
        )
    )
    active_meds = [
        {"name": m.name, "dosage": m.dosage, "start_date": str(m.start_date)}
        for m in result.scalars().all()
    ]

    prompt = f"""A patient reports: "{symptom.name}" with severity "{symptom.severity}".
Notes: {symptom.notes or "none"}

Their current active medications are: {json.dumps(active_meds)}

Return ONLY a valid JSON object with these exact keys:
- analysis: brief clinical interpretation (1-2 sentences)
- possible_causes: array of strings (include medication side effects if relevant)
- related_medications: array of medication names that could cause this symptom
- urgency: one of "routine", "see_doctor_soon", or "emergency"
- recommendation: what the patient should do"""

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
            return json.loads(response.choices[0].message.content)
        else:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"analysis": f"Analysis unavailable: {e}", "possible_causes": [], "related_medications": []}
