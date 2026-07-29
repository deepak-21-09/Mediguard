import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
import enum


class AppointmentStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    doctor_name: Mapped[str] = mapped_column(String(200))
    specialty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.UPCOMING
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI-generated summary for the appointment
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    questions_for_doctor: Mapped[list] = mapped_column(JSON, default=list)
    recent_medication_changes: Mapped[list] = mapped_column(JSON, default=list)
    recent_symptoms: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="appointments")
