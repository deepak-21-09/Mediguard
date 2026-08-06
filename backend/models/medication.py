import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
import enum


class MedicationStatus(str, enum.Enum):
    ACTIVE = "active"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class InteractionSeverity(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(300))
    generic_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    dosage: Mapped[str] = mapped_column(String(100))         # e.g. "500mg"
    frequency: Mapped[str] = mapped_column(String(100))      # e.g. "twice daily"
    route: Mapped[str | None] = mapped_column(String(50), nullable=True)  # oral, topical…
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    prescribing_doctor: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pharmacy: Mapped[str | None] = mapped_column(String(200), nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MedicationStatus] = mapped_column(
        Enum(MedicationStatus), default=MedicationStatus.ACTIVE
    )
    reminder_times: Mapped[list] = mapped_column(JSON, default=list)  # ["08:00","20:00"]
    ocr_source: Mapped[bool] = mapped_column(Boolean, default=False)
    prescription_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="medications")
    interactions: Mapped[list["DrugInteraction"]] = relationship(
        "DrugInteraction",
        foreign_keys="DrugInteraction.medication_a_id",
        back_populates="medication_a",
        cascade="all, delete-orphan",
    )


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    medication_a_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("medications.id", ondelete="CASCADE")
    )
    medication_b_name: Mapped[str] = mapped_column(String(300))
    interaction_type: Mapped[str] = mapped_column(String(50))  # drug-drug, drug-food, allergy
    severity: Mapped[InteractionSeverity] = mapped_column(Enum(InteractionSeverity))
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    medication_a: Mapped["Medication"] = relationship(
        "Medication", foreign_keys=[medication_a_id], back_populates="interactions"
    )
