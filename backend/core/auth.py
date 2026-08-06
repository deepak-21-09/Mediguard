"""
Auth helpers — three-tier JWT verification:
  1. Supabase JWT  (if SUPABASE_URL is configured)
  2. Clerk JWT     (if CLERK_SECRET_KEY is configured)
  3. Local HS256   (dev fallback)
"""
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a local HS256 JWT (used in dev/testing)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def _try_supabase(token: str) -> Optional[str]:
    """Verify against Supabase Auth. Returns user_id or None."""
    if not settings.is_supabase_configured:
        return None
    from core.supabase_client import verify_supabase_token
    payload = await verify_supabase_token(token)
    if payload:
        return payload.get("sub")
    return None


async def _try_clerk(token: str) -> Optional[str]:
    """Verify against Clerk JWKS. Returns user_id or None."""
    if not settings.CLERK_SECRET_KEY:
        return None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.clerk.dev/v1/jwks",
                headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"},
                timeout=5.0,
            )
            jwks = resp.json()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload.get("sub")
    except Exception:
        return None


def _try_local_jwt(token: str) -> Optional[str]:
    """
    Verify a locally-signed HS256 JWT. Returns user_id or None.
    Disabled in production unless SECRET_KEY has been replaced with a safe value
    (the startup check in main.py ensures a weak key can't reach this point, but
    we add a belt-and-suspenders guard here too).
    """
    if settings.ENVIRONMENT == "production" and not settings.is_secret_key_safe:
        # Should never be reached — validate_production_secrets() blocks startup first.
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    token = credentials.credentials

    # 1. Supabase
    user_id = await _try_supabase(token)
    if user_id:
        return await _verify_user_exists(user_id, db, credentials_exception)

    # 2. Clerk
    user_id = await _try_clerk(token)
    if user_id:
        return await _verify_user_exists(user_id, db, credentials_exception)

    # 3. Local JWT (dev)
    user_id = _try_local_jwt(token)
    if user_id:
        return await _verify_user_exists(user_id, db, credentials_exception)

    raise credentials_exception


async def _verify_user_exists(
    user_id: str,
    db: AsyncSession,
    exc: HTTPException,
) -> str:
    """
    Confirm the user_id from the token corresponds to an active User row.
    Rejects stale tokens for deleted accounts and fabricated sub claims.
    """
    from sqlalchemy import select
    from models.user import User

    result = await db.execute(
        select(User.id).where(User.id == user_id, User.is_active == True)
    )
    if result.scalar_one_or_none() is None:
        raise exc
    return user_id
