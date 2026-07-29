"""
PDF report generation using ReportLab.
"""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from sqlalchemy.ext.asyncio import AsyncSession

from models.medication import Medication
from models.symptom import Symptom
from models.profile import UserProfile
from models.user import User


async def generate_health_report(
    db: AsyncSession, user_id: str, include_symptoms: bool = True
) -> bytes:
    """Generate a PDF health report and return bytes."""
    from sqlalchemy import select

    # Fetch data
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    profile_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = profile_result.scalar_one_or_none()

    meds_result = await db.execute(
        select(Medication).where(Medication.user_id == user_id).order_by(Medication.created_at)
    )
    medications = meds_result.scalars().all()

    symptoms = []
    if include_symptoms:
        symp_result = await db.execute(
            select(Symptom)
            .where(Symptom.user_id == user_id)
            .order_by(Symptom.logged_at.desc())
            .limit(20)
        )
        symptoms = symp_result.scalars().all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"], fontSize=20, textColor=colors.HexColor("#1E3A5F")
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#2563EB")
    )
    normal_style = styles["Normal"]

    story = []

    # Header
    story.append(Paragraph("MediGuard Health Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}", normal_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563EB")))
    story.append(Spacer(1, 0.5 * cm))

    # Patient Info
    story.append(Paragraph("Patient Information", heading_style))
    patient_data = [
        ["Name", user.full_name if user else "N/A"],
        ["Email", user.email if user else "N/A"],
        ["Age", str(profile.age) if profile and profile.age else "N/A"],
        ["Blood Group", profile.blood_group if profile and profile.blood_group else "N/A"],
        ["Allergies", ", ".join(profile.allergies) if profile and profile.allergies else "None"],
        ["Conditions", ", ".join(profile.medical_conditions) if profile and profile.medical_conditions else "None"],
    ]
    table = Table(patient_data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF6FF")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # Medications
    story.append(Paragraph("Medication History", heading_style))
    if medications:
        med_data = [["Medication", "Dosage", "Frequency", "Status", "Start Date"]]
        for m in medications:
            med_data.append([
                m.name,
                m.dosage,
                m.frequency,
                m.status.value,
                str(m.start_date) if m.start_date else "-",
            ])
        med_table = Table(med_data, colWidths=[5 * cm, 3 * cm, 4 * cm, 3 * cm, 2.5 * cm])
        med_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(med_table)
    else:
        story.append(Paragraph("No medications recorded.", normal_style))
    story.append(Spacer(1, 0.5 * cm))

    # Symptoms
    if include_symptoms and symptoms:
        story.append(Paragraph("Recent Symptoms", heading_style))
        symp_data = [["Symptom", "Severity", "Date", "Notes"]]
        for s in symptoms:
            symp_data.append([
                s.name,
                s.severity.value,
                s.logged_at.strftime("%Y-%m-%d"),
                (s.notes or "")[:60],
            ])
        symp_table = Table(symp_data, colWidths=[5 * cm, 3 * cm, 3 * cm, 6.5 * cm])
        symp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(symp_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
