from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import User


# -----------------------------
# CREATE / UPDATE (UPSERT)
# -----------------------------
async def upsert_user(
    db: AsyncSession,
    *,
    user_id: str,  # Firebase UID
    display_name: Optional[str] = None,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> User:
    """
    Create a new user or update existing one if they already exist.
    Keeps data synced with Firebase.
    """
    res = await db.execute(select(User).where(User.user_id == user_id))
    user = res.scalar_one_or_none()

    if user is None:
        user = User(
            user_id=user_id,
            display_name=display_name,
            email=email,
            phone_number=phone_number,
            created_at=datetime.utcnow(),
        )
        db.add(user)
    else:
        await db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(
                display_name=display_name or user.display_name,
                email=email or user.email,
                phone_number=phone_number or user.phone_number
            )
        )

    await db.commit()
    await db.refresh(user)
    return user


# -----------------------------
# FETCH (READ)
# -----------------------------
async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """Return one user by their Firebase UID."""
    res = await db.execute(select(User).where(User.user_id == user_id))
    return res.scalar_one_or_none()


async def list_users(db: AsyncSession, limit: int = 100) -> Sequence[User]:
    """List latest registered users (for dashboard or debugging)."""
    res = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit)
    )
    return tuple(res.scalars().all())


# --- New Methods for API ---

class UsersRepo:
    """
    Static wrapper class for better import usage in endpoints.
    """
    @staticmethod
    async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
        return await get_user(db, user_id)

    @staticmethod
    async def create_user(
        db: AsyncSession, 
        user_id: str, 
        email: Optional[str] = None, 
        display_name: Optional[str] = None
    ) -> User:
        return await upsert_user(db, user_id=user_id, email=email, display_name=display_name)

    @staticmethod
    async def update_user(
        db: AsyncSession, 
        user_id: str, 
        email: Optional[str] = None, 
        display_name: Optional[str] = None,
        phone_number: Optional[str] = None

    ) -> User:
        return await upsert_user(db, user_id=user_id, email=email, display_name=display_name,phone_number=phone_number)