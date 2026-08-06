"""
Appointment service — CRUD + AI-generated pre-appointment summary.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.appointment import Appointment
from models.medication import Medication, MedicationStatus
from models.symptom import Symptom
from core.config import settings


async def list_appointments(db: AsyncSession, user_id: str) -> list[Appointment]:
    result = await db.execute(
        select(Appointment)
        .where(Appointment.user_id == user_id)
        .order_by(Appointment.scheduled_at)
    )
    return result.scalars().all()


async def create_appointment(db: AsyncSession, user_id: str, data: dict) -> Appointment:
    appt = Appointment(user_id=user_id, **data)
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


async def generate_appointment_summary(
    db: AsyncSession, user_id: str, appointment_id: str
) -> Appointment | None:
    """Generate an AI pre-appointment summary and attach it to the appointment."""
    result = await db.execute(
        select(Appointment).where(
            Appointment.user_id == user_id, Appointment.id == appointment_id
        )
    )
    appt = result.scalar_one_or_none()
    if not appt:
        return None

    # Collect context
    meds_result = await db.execute(
        select(Medication).where(
            Medication.user_id == user_id,
            Medication.status == MedicationStatus.ACTIVE,
        )
    )
    active_meds = [
        {"name": m.name, "dosage": m.dosage, "frequency": m.frequency, "purpose": m.purpose}
        for m in meds_result.scalars().all()
    ]

    since = datetime.utcnow() - timedelta(days=30)
    symp_result = await db.execute(
        select(Symptom)
        .where(Symptom.user_id == user_id, Symptom.logged_at >= since)
        .order_by(Symptom.logged_at.desc())
    )
    recent_symptoms = [
        {"name": s.name, "severity": s.severity, "date": s.logged_at.strftime("%Y-%m-%d")}
        for s in symp_result.scalars().all()
    ]

    prompt = f"""
A patient has an upcoming appointment with Dr. {appt.doctor_name} ({appt.specialty or 'General'}).
Appointment date: {appt.scheduled_at.strftime('%B %d, %Y')}

Current medications: {json.dumps(active_meds)}
Symptoms in last 30 days: {json.dumps(recent_symptoms)}

Generate a pre-appointment summary as JSON:
{{
  "summary": "2-3 sentence overview for the doctor",
  "key_concerns": ["list of key issues to discuss"],
  "questions_for_doctor": ["5 specific questions the patient should ask"],
  "medication_changes_to_discuss": ["any meds to review"],
  "recent_symptoms_summary": "brief paragraph about symptoms"
}}
    """

    provider = settings.effective_llm_provider
    try:
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
    except Exception as e:
        # Log server-side, return a generic message to the client.
        # Raw exception strings can leak API keys or internal stack info.
        import logging
        logging.getLogger("mediguard.appointments").warning(
            "AI summary generation failed for appointment %s: %s", appointment_id, e
        )
        appt.ai_summary = "AI summary temporarily unavailable. Please try again later."
        await db.commit()
        await db.refresh(appt)
        return appt

    data = json.loads(response.choices[0].message.content)
    appt.ai_summary = data.get("summary", "")
    appt.questions_for_doctor = data.get("questions_for_doctor", [])
    appt.recent_symptoms = [data.get("recent_symptoms_summary", "")]
    appt.recent_medication_changes = data.get("medication_changes_to_discuss", [])

    await db.commit()
    await db.refresh(appt)
    return appt
