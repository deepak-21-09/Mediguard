import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # stored as JSON arrays
    medical_conditions: Mapped[list] = mapped_column(JSON, default=list)
    allergies: Mapped[list] = mapped_column(JSON, default=list)
    current_diseases: Mapped[list] = mapped_column(JSON, default=list)

    emergency_contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emergency_contact_relation: Mapped[str | None] = mapped_column(String(50), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")
