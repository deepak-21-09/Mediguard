"""
Health dashboard — aggregated stats for the home screen.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user_id
from models.medication import Medication, MedicationStatus, DrugInteraction, InteractionSeverity
from models.symptom import Symptom
from models.appointment import Appointment, AppointmentStatus
from models.reminder import Reminder, ReminderStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Active medications
    active_meds_result = await db.execute(
        select(Medication).where(
            Medication.user_id == user_id,
            Medication.status == MedicationStatus.ACTIVE,
        )
    )
    active_meds = active_meds_result.scalars().all()

    # Today's reminders
    reminders_result = await db.execute(
        select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.scheduled_at >= today_start,
            Reminder.scheduled_at < today_start + timedelta(days=1),
        )
    )
    todays_reminders = reminders_result.scalars().all()
    missed = [r for r in todays_reminders if r.status == ReminderStatus.MISSED]
    completed = [r for r in todays_reminders if r.status == ReminderStatus.COMPLETED]

    # Recent symptoms (7 days)
    symp_result = await db.execute(
        select(Symptom).where(
            Symptom.user_id == user_id,
            Symptom.logged_at >= now - timedelta(days=7),
        ).order_by(Symptom.logged_at.desc()).limit(5)
    )
    recent_symptoms = symp_result.scalars().all()

    # Active interactions
    interactions_result = await db.execute(
        select(DrugInteraction).where(
            DrugInteraction.user_id == user_id,
            DrugInteraction.is_acknowledged == False,
        )
    )
    active_interactions = interactions_result.scalars().all()
    critical_count = sum(
        1 for i in active_interactions
        if i.severity in (InteractionSeverity.HIGH, InteractionSeverity.CRITICAL)
    )

    # Next appointment
    appt_result = await db.execute(
        select(Appointment).where(
            Appointment.user_id == user_id,
            Appointment.status == AppointmentStatus.UPCOMING,
            Appointment.scheduled_at >= now,
        ).order_by(Appointment.scheduled_at).limit(1)
    )
    next_appt = appt_result.scalar_one_or_none()

    # Health score (simple heuristic)
    score = 100
    score -= len(missed) * 5
    score -= critical_count * 15
    score -= len([s for s in recent_symptoms if s.severity.value in ("severe", "critical")]) * 10
    score = max(0, min(100, score))

    return {
        "active_medications": len(active_meds),
        "todays_medications": [
            {"name": m.name, "dosage": m.dosage, "frequency": m.frequency}
            for m in active_meds
        ],
        "todays_reminders": {
            "total": len(todays_reminders),
            "completed": len(completed),
            "missed": len(missed),
        },
        "recent_symptoms": [
            {"name": s.name, "severity": s.severity.value, "logged_at": s.logged_at}
            for s in recent_symptoms
        ],
        "risk_alerts": {
            "total_interactions": len(active_interactions),
            "critical_interactions": critical_count,
        },
        "next_appointment": {
            "doctor": next_appt.doctor_name,
            "scheduled_at": next_appt.scheduled_at,
        } if next_appt else None,
        "health_score": score,
    }
