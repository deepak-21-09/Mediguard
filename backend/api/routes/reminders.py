from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
from typing import Optional

from core.database import get_db
from core.auth import get_current_user_id
from models.reminder import Reminder, ReminderType, ReminderStatus

router = APIRouter(prefix="/reminders", tags=["reminders"])


class ReminderCreate(BaseModel):
    title: str
    message: Optional[str] = None
    reminder_type: str = "medication"
    medication_id: Optional[str] = None
    scheduled_at: datetime
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None

    @field_validator("scheduled_at", mode="after")
    @classmethod
    def strip_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v


class ReminderUpdate(BaseModel):
    status: Optional[str] = None
    snoozed_until: Optional[datetime] = None


@router.get("")
async def get_reminders(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .order_by(Reminder.scheduled_at)
    )
    return result.scalars().all()


@router.post("", status_code=201)
async def create_reminder(
    data: ReminderCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    reminder = Reminder(
        user_id=user_id,
        title=data.title,
        message=data.message,
        reminder_type=ReminderType(data.reminder_type),
        medication_id=data.medication_id,
        scheduled_at=data.scheduled_at,
        is_recurring=data.is_recurring,
        recurrence_rule=data.recurrence_rule,
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.patch("/{reminder_id}")
async def update_reminder(
    reminder_id: str,
    data: ReminderUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    if data.status:
        reminder.status = ReminderStatus(data.status)
        if data.status == "completed":
            reminder.completed_at = datetime.utcnow()
    if data.snoozed_until:
        reminder.snoozed_until = data.snoozed_until
        reminder.status = ReminderStatus.SNOOZED

    await db.commit()
    await db.refresh(reminder)
    return reminder
