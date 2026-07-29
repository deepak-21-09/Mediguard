from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user_id
from services.appointment_service import (
    list_appointments,
    create_appointment,
    generate_appointment_summary,
)
from api.schemas import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentOut])
async def get_appointments(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await list_appointments(db, user_id)


@router.post("", response_model=AppointmentOut, status_code=201)
async def add_appointment(
    data: AppointmentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await create_appointment(db, user_id, data.model_dump())


@router.post("/{appointment_id}/summary", response_model=AppointmentOut)
async def get_appointment_summary(
    appointment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate or refresh AI pre-appointment summary."""
    appt = await generate_appointment_summary(db, user_id, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt
