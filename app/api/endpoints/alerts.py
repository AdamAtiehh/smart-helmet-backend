from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.auth import get_current_user_uid
from app.repositories.alerts_repo import recent_for_user, resolve_alert, get_by_id
from app.models.schemas import AlertOut

router = APIRouter()

@router.get("", response_model=List[AlertOut])
async def list_my_alerts(
    limit: int = 50,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    List recent alerts for the current user.
    """
    alerts = await recent_for_user(db, uid, limit=limit)
    return alerts

@router.post("/{alert_id}/ack")
async def acknowledge_alert(
    alert_id: str,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    Acknowledge (resolve) an alert.
    """
    alert = await get_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.user_id != uid:
        raise HTTPException(status_code=403, detail="Not authorized to manage this alert")
        
    await resolve_alert(db, alert_id, resolved_by=uid)
    await db.commit()
    
    return {"status": "resolved", "alert_id": alert_id}
