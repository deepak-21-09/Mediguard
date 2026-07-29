"""
Storage service — uploads files to Supabase Storage when configured,
falls back to local filesystem (/tmp) for dev.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime

from core.config import settings


async def save_prescription_image(
    user_id: str,
    file_bytes: bytes,
    content_type: str = "image/jpeg",
) -> str:
    """
    Save a prescription image.
    Returns: a URL or local path string.
    """
    ext = _ext_from_content_type(content_type)
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"

    if settings.is_supabase_configured:
        from core.supabase_client import upload_prescription
        url = await upload_prescription(user_id, filename, file_bytes, content_type)
        return url
    else:
        # Local fallback
        path = os.path.join("/tmp", f"{user_id}_{filename}")
        with open(path, "wb") as f:
            f.write(file_bytes)
        return f"local://{path}"


async def save_report_pdf(user_id: str, pdf_bytes: bytes) -> str:
    """
    Save a generated PDF report.
    Returns: a URL or local path string.
    """
    filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

    if settings.is_supabase_configured:
        from core.supabase_client import upload_report
        url = await upload_report(user_id, filename, pdf_bytes)
        return url
    else:
        path = os.path.join("/tmp", f"{user_id}_{filename}")
        with open(path, "wb") as f:
            f.write(pdf_bytes)
        return f"local://{path}"


def _ext_from_content_type(ct: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return mapping.get(ct.lower(), ".jpg")
