# app/api/endpoints/trips.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.models.schemas import TripSummaryOut, TripDetailOut, RoutePoint, TripDataRead
from app.database.connection import get_db
from app.services.auth import get_current_user_uid
from app.repositories.trips_repo import TripsRepo
import app.repositories.telemetry_repo as TelemetryRepo

router = APIRouter()

# --- Endpoints ---

@router.get("", response_model=List[TripSummaryOut])
async def list_my_trips(
    limit: int = 20,
    offset: int = 0,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    List trips for the current user.
    """
    # We need a method in TripsRepo to get trips by user_id.
    # Assuming TripsRepo.get_user_trips exists or we will add it.
    # For now, I'll assume we need to add it or use a direct query if needed.
    # I'll use a static method wrapper pattern again if needed, but let's check repo first?
    # No, let's just implement the endpoint and then fix the repo like before.
    
    trips = await TripsRepo.get_user_trips(db, uid, limit=limit, offset=offset)
    
    return [
        TripSummaryOut(
            trip_id=t.trip_id,
            device_id=t.device_id,
            start_time=t.start_time,
            end_time=t.end_time,
            # total_distance=t.total_distance,
            # average_speed=t.average_speed,
            status=t.status
        ) for t in trips
    ]

@router.get("/{trip_id}", response_model=TripDetailOut)
async def get_trip_details(
    trip_id: str,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed summary of a trip.
    """
    trip = await TripsRepo.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.user_id != uid:
        raise HTTPException(status_code=403, detail="Not authorized to view this trip")
        
    return TripDetailOut(
        trip_id=trip.trip_id,
        device_id=trip.device_id,
        start_time=trip.start_time,
        end_time=trip.end_time,
        total_distance=trip.total_distance,
        average_speed=trip.average_speed,
        status=trip.status,
        max_speed=trip.max_speed,
        average_heart_rate=trip.average_heart_rate,
        start_lat=trip.start_lat,
        start_lng=trip.start_lng,
        end_lat=trip.end_lat,
        end_lng=trip.end_lng
    )

@router.get("/{trip_id}/route", response_model=List[RoutePoint])
async def get_trip_route(
    trip_id: str,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the full GPS route for a trip.
    """
    trip = await TripsRepo.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.user_id != uid:
        raise HTTPException(status_code=403, detail="Not authorized to view this trip")
        
    # Fetch route points
    points = await TripsRepo.get_trip_route_points(db, trip_id)
    
    return [
        RoutePoint(
            lat=p.lat,
            lng=p.lng,
            ts=p.timestamp,
            speed=p.speed
        ) for p in points
    ]

@router.get("/{trip_id}/metrics", response_model=List[TripDataRead])
async def get_trip_metrics(
    trip_id: str,
    limit: int = 1000,
    offset: int = 0,
    uid: str = Depends(get_current_user_uid),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full telemetry data for a trip (paginated).
    """
    trip = await TripsRepo.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.user_id != uid:
        raise HTTPException(status_code=403, detail="Not authorized to view this trip")
        
    # Fetch telemetry
    data = await TelemetryRepo.get_range_for_trip(db, trip_id, limit=limit, offset=offset)
    return data
