"""
Auth routes — supports three flows:
  1. Supabase Auth  (register/login via Supabase, sync user to our DB)
  2. Clerk webhook  (sync Clerk user to our DB)
  3. Local dev JWT  (dev-only, no external auth)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.config import settings
from core.auth import create_access_token
from models.user import User
from models.profile import UserProfile
from api.schemas import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Supabase Auth ─────────────────────────────────────────────────────────────

class SupabaseRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str = ""


class SupabaseLoginRequest(BaseModel):
    email: str
    password: str


@router.post("/supabase/register", response_model=dict, status_code=201)
async def supabase_register(
    data: SupabaseRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user via Supabase Auth, then sync to MediGuard DB.
    Returns a Supabase session (access_token).
    """
    if not settings.is_supabase_configured:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured on this server.",
        )

    from supabase import create_client
    # Use anon key for sign-up (user-facing operation)
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    try:
        response = sb.auth.sign_up({
            "email": data.email,
            "password": data.password,
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not response.user:
        raise HTTPException(status_code=400, detail="Registration failed.")

    supabase_uid = response.user.id

    # Sync to MediGuard users table
    existing = await db.execute(select(User).where(User.clerk_id == supabase_uid))
    user = existing.scalar_one_or_none()

    if not user:
        user = User(
            clerk_id=supabase_uid,  # reuse clerk_id column for any external auth UID
            email=data.email,
            full_name=data.full_name,
            phone=data.phone or None,
        )
        db.add(user)
        await db.flush()
        db.add(UserProfile(user_id=user.id))
        await db.commit()
        await db.refresh(user)

    session = response.session
    return {
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
        "access_token": session.access_token if session else None,
        "token_type": "bearer",
        "provider": "supabase",
    }


@router.post("/supabase/login", response_model=dict)
async def supabase_login(
    data: SupabaseLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login via Supabase Auth and return access token."""
    if not settings.is_supabase_configured:
        raise HTTPException(status_code=503, detail="Supabase is not configured.")

    from supabase import create_client
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    try:
        response = sb.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password,
        })
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    if not response.user or not response.session:
        raise HTTPException(status_code=401, detail="Login failed.")

    supabase_uid = response.user.id

    # Ensure user exists in our DB
    result = await db.execute(select(User).where(User.clerk_id == supabase_uid))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            clerk_id=supabase_uid,
            email=response.user.email,
            full_name=response.user.email.split("@")[0],
        )
        db.add(user)
        await db.flush()
        db.add(UserProfile(user_id=user.id))
        await db.commit()
        await db.refresh(user)

    return {
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "token_type": "bearer",
        "provider": "supabase",
    }


@router.post("/supabase/refresh", response_model=dict)
async def supabase_refresh(refresh_token: str):
    """Refresh a Supabase session using a refresh token."""
    if not settings.is_supabase_configured:
        raise HTTPException(status_code=503, detail="Supabase is not configured.")

    from supabase import create_client
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    try:
        response = sb.auth.refresh_session(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Could not refresh session.")

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "token_type": "bearer",
    }


# ── Clerk sync ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register or sync a Clerk user to the MediGuard DB."""
    result = await db.execute(select(User).where(User.clerk_id == data.clerk_id))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    user = User(clerk_id=data.clerk_id, email=data.email, full_name=data.full_name, phone=data.phone)
    db.add(user)
    await db.flush()
    db.add(UserProfile(user_id=user.id))
    await db.commit()
    await db.refresh(user)
    return user


# ── Local dev JWT ─────────────────────────────────────────────────────────────

@router.post("/token")
async def get_token(clerk_id: str, db: AsyncSession = Depends(get_db)):
    """Dev-only: exchange a clerk_id for a local JWT."""
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


# ── Supabase status ───────────────────────────────────────────────────────────

@router.get("/supabase/status")
async def supabase_status():
    """Check if Supabase is configured and reachable."""
    if not settings.is_supabase_configured:
        return {"configured": False, "message": "Supabase credentials not set."}
    try:
        from core.supabase_client import get_supabase
        client = get_supabase()
        # Lightweight auth check — doesn't require any specific table
        client.auth.get_session()
        return {"configured": True, "url": settings.SUPABASE_URL, "status": "connected"}
    except Exception as e:
        # Even an "empty session" response means we connected successfully
        err = str(e).lower()
        if "session" in err or "no session" in err or "auth" in err:
            return {"configured": True, "url": settings.SUPABASE_URL, "status": "connected"}
        return {"configured": True, "url": settings.SUPABASE_URL, "status": "error", "detail": str(e)}
