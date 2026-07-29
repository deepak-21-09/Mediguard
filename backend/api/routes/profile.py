from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.auth import get_current_user_id
from models.profile import UserProfile
from models.user import User
from api.schemas import ProfileUpsert, ProfileOut, EmergencyCard
from models.medication import Medication, MedicationStatus

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("", response_model=ProfileOut)
async def upsert_profile(
    data: ProfileUpsert,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/emergency-card", response_model=EmergencyCard)
async def get_emergency_card(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """One-tap emergency info — no auth required in a real emergency scenario."""
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = profile_result.scalar_one_or_none()

    meds_result = await db.execute(
        select(Medication).where(
            Medication.user_id == user_id,
            Medication.status == MedicationStatus.ACTIVE,
        )
    )
    active_meds = meds_result.scalars().all()

    return EmergencyCard(
        full_name=user.full_name if user else "Unknown",
        blood_group=profile.blood_group if profile else None,
        allergies=profile.allergies if profile else [],
        active_medications=[
            {"name": m.name, "dosage": m.dosage, "frequency": m.frequency}
            for m in active_meds
        ],
        emergency_contact_name=profile.emergency_contact_name if profile else None,
        emergency_contact_phone=profile.emergency_contact_phone if profile else None,
        medical_conditions=profile.medical_conditions if profile else [],
    )
