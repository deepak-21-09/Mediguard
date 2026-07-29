import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    clerk_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    medications: Mapped[list["Medication"]] = relationship(
        "Medication", back_populates="user", cascade="all, delete-orphan"
    )
    symptoms: Mapped[list["Symptom"]] = relationship(
        "Symptom", back_populates="user", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="user", cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="user", cascade="all, delete-orphan"
    )
