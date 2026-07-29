"""
Supabase client — wraps the official supabase-py SDK.
Used for:
  - Storage (prescription images, PDF reports)
  - Auth token verification (Supabase JWT)
  - Realtime (future)

The client is a lazy singleton — only initialised when
SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set.
"""
from __future__ import annotations

import io
from typing import Optional
from core.config import settings

_client = None


def get_supabase():
    """Return the Supabase admin client (service role)."""
    global _client
    if _client is None:
        if not settings.is_supabase_configured:
            raise RuntimeError(
                "Supabase is not configured. Set SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY in your .env file."
            )
        from supabase import create_client
        _client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _client


# ── Storage helpers ───────────────────────────────────────────────────────────

async def upload_prescription(
    user_id: str,
    filename: str,
    file_bytes: bytes,
    content_type: str = "image/jpeg",
) -> str:
    """
    Upload a prescription image to Supabase Storage.
    Returns the public URL.
    """
    client = get_supabase()
    bucket = settings.SUPABASE_STORAGE_BUCKET_PRESCRIPTIONS
    path = f"{user_id}/{filename}"

    client.storage.from_(bucket).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    result = client.storage.from_(bucket).get_public_url(path)
    return result


async def upload_report(
    user_id: str,
    filename: str,
    pdf_bytes: bytes,
) -> str:
    """
    Upload a generated PDF report to Supabase Storage.
    Returns the public URL.
    """
    client = get_supabase()
    bucket = settings.SUPABASE_STORAGE_BUCKET_REPORTS
    path = f"{user_id}/{filename}"

    client.storage.from_(bucket).upload(
        path=path,
        file=pdf_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )
    result = client.storage.from_(bucket).get_public_url(path)
    return result


async def delete_file(bucket: str, path: str) -> None:
    """Delete a file from a Supabase Storage bucket."""
    client = get_supabase()
    client.storage.from_(bucket).remove([path])


# ── Auth helpers ──────────────────────────────────────────────────────────────

async def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verify a Supabase JWT and return the user payload.
    Returns None if invalid.
    """
    if not settings.is_supabase_configured:
        return None
    try:
        client = get_supabase()
        response = client.auth.get_user(token)
        if response and response.user:
            return {
                "sub": response.user.id,
                "email": response.user.email,
                "provider": "supabase",
            }
    except Exception:
        pass
    return None


async def create_supabase_user(email: str, password: str) -> dict:
    """Create a new user via Supabase Auth (admin API)."""
    client = get_supabase()
    response = client.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,
    })
    return {"id": response.user.id, "email": response.user.email}
