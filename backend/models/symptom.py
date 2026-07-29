import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
import enum


class SymptomSeverity(str, enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class Symptom(Base):
    __tablename__ = "symptoms"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    severity: Mapped[SymptomSeverity] = mapped_column(Enum(SymptomSeverity))
    severity_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10
    body_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI analysis result
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    possible_causes: Mapped[list] = mapped_column(JSON, default=list)
    related_medications: Mapped[list] = mapped_column(JSON, default=list)

    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="symptoms")
