# app/services/auth.py
from __future__ import annotations

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials

# Initialize Firebase Admin SDK
# In production, you would provide the path to your service account JSON
# via an environment variable or direct path.
# For this MVP, we'll allow a mock mode if no creds are found.

cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not firebase_admin._apps:
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print(f"[auth] Firebase Admin initialized with {cred_path}")
    else:
        print("[auth] WARNING: No Firebase credentials found. Auth will be MOCKED.")

security = HTTPBearer()

async def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extracts the Bearer token from the Authorization header.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

async def verify_firebase_token(token: str) -> dict:
    """
    Verifies the Firebase ID token.
    If Firebase is not initialized (mock mode), accepts any token starting with 'mock_'.
    """
    # MOCK MODE
    if not firebase_admin._apps:
        if token.startswith("mock_"):
            # Simulate a decoded token
            return {
                "uid": f"user_{token}",
                "email": "mock@example.com",
                "name": "Mock User"
            }
        else:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid mock token. Use 'mock_...'",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # REAL MODE
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_uid(token: str = Depends(get_current_user_token)) -> str:
    """
    Dependency to get the current user's UID.
    """
    decoded = await verify_firebase_token(token)
    return decoded.get("uid")
