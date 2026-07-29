"""
Medication service — CRUD + AI drug interaction check on every add/update.
"""
from __future__ import annotations

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.medication import Medication, DrugInteraction, MedicationStatus, InteractionSeverity
from memory.hindsight import HindsightMemory
from agents.tools import check_drug_interaction, configure_tools


async def list_medications(db: AsyncSession, user_id: str) -> list[Medication]:
    result = await db.execute(
        select(Medication)
        .where(Medication.user_id == user_id)
        .order_by(Medication.created_at.desc())
    )
    return result.scalars().all()


async def get_medication(db: AsyncSession, user_id: str, med_id: str) -> Medication | None:
    result = await db.execute(
        select(Medication).where(
            Medication.user_id == user_id, Medication.id == med_id
        )
    )
    return result.scalar_one_or_none()


async def create_medication(
    db: AsyncSession,
    user_id: str,
    data: dict,
    memory: HindsightMemory,
) -> tuple[Medication, list[DrugInteraction]]:
    med = Medication(user_id=user_id, **data)
    db.add(med)
    await db.flush()  # get the ID

    # Check interactions
    interactions = await _run_interaction_check(db, user_id, med, memory)

    # Store in Hindsight memory
    await memory.store(
        user_id=user_id,
        memory_type="medication",
        content=(
            f"Started medication: {med.name} {med.dosage} {med.frequency}. "
            f"Purpose: {med.purpose or 'not specified'}. "
            f"Doctor: {med.prescribing_doctor or 'not specified'}."
        ),
        metadata={
            "medication_id": med.id,
            "status": med.status,
            "start_date": str(med.start_date) if med.start_date else None,
        },
    )

    await db.commit()
    await db.refresh(med)
    return med, interactions


async def update_medication(
    db: AsyncSession, user_id: str, med_id: str, data: dict
) -> Medication | None:
    med = await get_medication(db, user_id, med_id)
    if not med:
        return None
    for key, value in data.items():
        setattr(med, key, value)
    await db.commit()
    await db.refresh(med)
    return med


async def delete_medication(db: AsyncSession, user_id: str, med_id: str) -> bool:
    med = await get_medication(db, user_id, med_id)
    if not med:
        return False
    await db.delete(med)
    await db.commit()
    return True


async def _run_interaction_check(
    db: AsyncSession, user_id: str, new_med: Medication, memory: HindsightMemory
) -> list[DrugInteraction]:
    """Run AI interaction check and persist results."""
    configure_tools(user_id=user_id, db_session=db, memory=memory)
    raw = await check_drug_interaction.ainvoke({"new_drug": new_med.name})

    try:
        data = json.loads(raw)
        interactions_data = data if isinstance(data, list) else data.get("interactions", [])
    except Exception:
        return []

    saved = []
    for item in interactions_data:
        severity_str = item.get("severity", "low").lower()
        try:
            severity = InteractionSeverity(severity_str)
        except ValueError:
            severity = InteractionSeverity.LOW

        interaction = DrugInteraction(
            user_id=user_id,
            medication_a_id=new_med.id,
            medication_b_name=item.get("medication_b", "unknown"),
            interaction_type=item.get("interaction_type", "drug-drug"),
            severity=severity,
            description=item.get("description", ""),
            recommendation=item.get("recommendation", ""),
        )
        db.add(interaction)
        saved.append(interaction)

        # Store critical interactions in memory
        if severity in (InteractionSeverity.HIGH, InteractionSeverity.CRITICAL):
            await memory.store(
                user_id=user_id,
                memory_type="event",
                content=(
                    f"INTERACTION ALERT: {new_med.name} has a {severity} interaction "
                    f"with {item.get('medication_b', 'unknown')}. "
                    f"{item.get('description', '')}"
                ),
                metadata={"severity": severity, "type": "drug_interaction"},
            )

    await db.flush()
    return saved
