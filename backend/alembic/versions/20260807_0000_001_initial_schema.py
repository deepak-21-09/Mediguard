"""initial_schema

Revision ID: 001
Revises:
Create Date: 2026-08-07 00:00:00.000000

Hand-crafted initial migration representing the full schema as defined by the
SQLAlchemy models at the time this file was generated.  Includes the three
recently-added indexes:
  - ix_drug_interactions_user_id   (DrugInteraction.user_id)
  - ix_user_profiles_user_id       (UserProfile.user_id)
  - ix_chat_sessions_updated_at    (ChatSession.updated_at)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("clerk_id", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_clerk_id", "users", ["clerk_id"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # user_profiles
    # ------------------------------------------------------------------
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("blood_group", sa.String(10), nullable=True),
        sa.Column("medical_conditions", sa.JSON(), nullable=False),
        sa.Column("allergies", sa.JSON(), nullable=False),
        sa.Column("current_diseases", sa.JSON(), nullable=False),
        sa.Column("emergency_contact_name", sa.String(200), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(20), nullable=True),
        sa.Column("emergency_contact_relation", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    # Recently-added index (one of the three requested)
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # medications
    # ------------------------------------------------------------------
    op.create_table(
        "medications",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("generic_name", sa.String(300), nullable=True),
        sa.Column("dosage", sa.String(100), nullable=False),
        sa.Column("frequency", sa.String(100), nullable=False),
        sa.Column("route", sa.String(50), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("prescribing_doctor", sa.String(200), nullable=True),
        sa.Column("pharmacy", sa.String(200), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "stopped", "completed", "on_hold", name="medicationstatus"),
            nullable=False,
        ),
        sa.Column("reminder_times", sa.JSON(), nullable=False),
        sa.Column("ocr_source", sa.Boolean(), nullable=False),
        sa.Column("prescription_image_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medications_user_id", "medications", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # drug_interactions
    # ------------------------------------------------------------------
    op.create_table(
        "drug_interactions",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("medication_a_id", sa.String(36), nullable=False),
        sa.Column("medication_b_name", sa.String(300), nullable=False),
        sa.Column("interaction_type", sa.String(50), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("low", "moderate", "high", "critical", name="interactionseverity"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("is_acknowledged", sa.Boolean(), nullable=False),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["medication_a_id"], ["medications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Recently-added index (one of the three requested)
    op.create_index("ix_drug_interactions_user_id", "drug_interactions", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # symptoms
    # ------------------------------------------------------------------
    op.create_table(
        "symptoms",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("mild", "moderate", "severe", "critical", name="symptomseverity"),
            nullable=False,
        ),
        sa.Column("severity_score", sa.Integer(), nullable=True),
        sa.Column("body_location", sa.String(100), nullable=True),
        sa.Column("duration_hours", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("possible_causes", sa.JSON(), nullable=False),
        sa.Column("related_medications", sa.JSON(), nullable=False),
        sa.Column("logged_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_symptoms_user_id", "symptoms", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # reminders
    # ------------------------------------------------------------------
    op.create_table(
        "reminders",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("medication_id", sa.String(36), nullable=True),
        sa.Column(
            "reminder_type",
            sa.Enum("medication", "appointment", "refill", "lab_test", name="remindertype"),
            nullable=False,
        ),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("message", sa.String(500), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "sent", "completed", "missed", "snoozed", name="reminderstatus"),
            nullable=False,
        ),
        sa.Column("is_recurring", sa.Boolean(), nullable=False),
        sa.Column("recurrence_rule", sa.String(100), nullable=True),
        sa.Column("snoozed_until", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["medication_id"], ["medications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"], unique=False)
    op.create_index("ix_reminders_scheduled_at", "reminders", ["scheduled_at"], unique=False)

    # ------------------------------------------------------------------
    # appointments
    # ------------------------------------------------------------------
    op.create_table(
        "appointments",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("doctor_name", sa.String(200), nullable=False),
        sa.Column("specialty", sa.String(100), nullable=True),
        sa.Column("location", sa.String(300), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("upcoming", "completed", "cancelled", name="appointmentstatus"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("questions_for_doctor", sa.JSON(), nullable=False),
        sa.Column("recent_medication_changes", sa.JSON(), nullable=False),
        sa.Column("recent_symptoms", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_user_id", "appointments", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # chat_sessions
    # ------------------------------------------------------------------
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"], unique=False)
    # Recently-added index (one of the three requested)
    op.create_index("ix_chat_sessions_updated_at", "chat_sessions", ["updated_at"], unique=False)

    # ------------------------------------------------------------------
    # chat_messages
    # ------------------------------------------------------------------
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", "system", name="messagerole"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("extra_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index("ix_chat_sessions_updated_at", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_user_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")

    op.drop_index("ix_appointments_user_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_reminders_scheduled_at", table_name="reminders")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_table("reminders")

    op.drop_index("ix_symptoms_user_id", table_name="symptoms")
    op.drop_table("symptoms")

    op.drop_index("ix_drug_interactions_user_id", table_name="drug_interactions")
    op.drop_table("drug_interactions")

    op.drop_index("ix_medications_user_id", table_name="medications")
    op.drop_table("medications")

    op.drop_index("ix_user_profiles_user_id", table_name="user_profiles")
    op.drop_table("user_profiles")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_clerk_id", table_name="users")
    op.drop_table("users")

    # Drop Enum types (PostgreSQL keeps them as named types)
    op.execute("DROP TYPE IF EXISTS medicationstatus")
    op.execute("DROP TYPE IF EXISTS interactionseverity")
    op.execute("DROP TYPE IF EXISTS symptomseverity")
    op.execute("DROP TYPE IF EXISTS remindertype")
    op.execute("DROP TYPE IF EXISTS reminderstatus")
    op.execute("DROP TYPE IF EXISTS appointmentstatus")
    op.execute("DROP TYPE IF EXISTS messagerole")
