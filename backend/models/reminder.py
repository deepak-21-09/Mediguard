import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Time, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
import enum


class ReminderType(str, enum.Enum):
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    REFILL = "refill"
    LAB_TEST = "lab_test"


class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    COMPLETED = "completed"
    MISSED = "missed"
    SNOOZED = "snoozed"


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    medication_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("medications.id", ondelete="SET NULL"), nullable=True
    )
    reminder_type: Mapped[ReminderType] = mapped_column(Enum(ReminderType))
    title: Mapped[str] = mapped_column(String(300))
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus), default=ReminderStatus.PENDING
    )
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)  # cron-like
    snoozed_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="reminders")
