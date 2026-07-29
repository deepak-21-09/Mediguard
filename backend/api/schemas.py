"""
Pydantic schemas for request/response validation.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ── Users / Auth ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    clerk_id: str
    email: str
    full_name: str
    phone: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileUpsert(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_group: Optional[str] = None
    medical_conditions: list[str] = []
    allergies: list[str] = []
    current_diseases: list[str] = []
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    notes: Optional[str] = None


class ProfileOut(ProfileUpsert):
    id: str
    user_id: str
    model_config = {"from_attributes": True}


# ── Medications ───────────────────────────────────────────────────────────────

class MedicationCreate(BaseModel):
    name: str
    generic_name: Optional[str] = None
    dosage: str
    frequency: str
    route: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    prescribing_doctor: Optional[str] = None
    pharmacy: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    reminder_times: list[str] = []


class MedicationUpdate(BaseModel):
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    reminder_times: Optional[list[str]] = None


class InteractionOut(BaseModel):
    id: str
    medication_b_name: str
    interaction_type: str
    severity: str
    description: str
    recommendation: str
    detected_at: datetime
    model_config = {"from_attributes": True}


class MedicationOut(BaseModel):
    id: str
    name: str
    generic_name: Optional[str]
    dosage: str
    frequency: str
    route: Optional[str]
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    prescribing_doctor: Optional[str]
    pharmacy: Optional[str]
    purpose: Optional[str]
    notes: Optional[str]
    reminder_times: list[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Symptoms ──────────────────────────────────────────────────────────────────

class SymptomCreate(BaseModel):
    name: str
    severity: str
    severity_score: Optional[int] = Field(None, ge=1, le=10)
    body_location: Optional[str] = None
    duration_hours: Optional[int] = None
    notes: Optional[str] = None
    logged_at: Optional[datetime] = None


class SymptomOut(BaseModel):
    id: str
    name: str
    severity: str
    severity_score: Optional[int]
    body_location: Optional[str]
    notes: Optional[str]
    ai_analysis: Optional[str]
    possible_causes: list[Any]
    related_medications: list[Any]
    logged_at: datetime
    model_config = {"from_attributes": True}


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


# ── Appointments ──────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    doctor_name: str
    specialty: Optional[str] = None
    location: Optional[str] = None
    scheduled_at: datetime
    notes: Optional[str] = None

    @field_validator("scheduled_at", mode="after")
    @classmethod
    def strip_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v


class AppointmentOut(BaseModel):
    id: str
    doctor_name: str
    specialty: Optional[str]
    location: Optional[str]
    scheduled_at: datetime
    status: str
    ai_summary: Optional[str]
    questions_for_doctor: list[Any]
    recent_symptoms: list[Any]
    recent_medication_changes: list[Any]
    notes: Optional[str]
    model_config = {"from_attributes": True}


# ── Emergency Card ────────────────────────────────────────────────────────────

class EmergencyCard(BaseModel):
    full_name: str
    blood_group: Optional[str]
    allergies: list[str]
    active_medications: list[dict]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    medical_conditions: list[str]
