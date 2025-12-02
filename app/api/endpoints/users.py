# app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from app.models.schemas import UserRead, UserUpdate
from app.database.connection import get_db
from app.services.auth import get_current_user_uid
from app.repositories.users_repo import UsersRepo

router = APIRouter()

# --- Endpoints ---

@router.get("/me", response_model=UserRead)
async def get_my_profile(
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current logged-in user's profile.
    If user doesn't exist in DB yet (first login), create them.
    """
    user = await UsersRepo.get_user(db, uid)
    if not user:
        # Auto-create user if they authenticated via Firebase but aren't in our DB
        # In a real app, you might want to fetch email/name from Firebase token here
        user = await UsersRepo.create_user(db, uid, email=None, display_name="New User")
    
    return user

@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    update_data: UserUpdate,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    """
    user = await UsersRepo.update_user(db, uid, **update_data.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user
