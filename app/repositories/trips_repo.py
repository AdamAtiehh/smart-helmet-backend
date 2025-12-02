from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Trip


# -------------------------------
# CREATE / CLOSE / FETCH TRIPS
# -------------------------------

async def create_trip(
    db: AsyncSession,
    user_id: Optional[str],
    device_id: str,
    start_time: datetime,
    start_lat: Optional[float] = None,
    start_lng: Optional[float] = None,
) -> Trip:
    """
    Create a new trip entry when a trip_start message arrives.
    Returns the Trip object (not yet committed).
    """
    trip = Trip(
        user_id=user_id,
        device_id=device_id,
        start_time=start_time,
        start_lat=start_lat,
        start_lng=start_lng,
        status="recording",
    )
    db.add(trip)
    await db.flush()  # to get trip_id populated
    return trip


async def close_trip(
    db: AsyncSession,
    trip_id: str,
    end_time: datetime,
    end_lat: Optional[float] = None,
    end_lng: Optional[float] = None,
    crash_detected: Optional[bool] = None,
) -> None:
    """
    Mark a trip as completed (called when trip_end message arrives).
    """
    await db.execute(
        update(Trip)
        .where(Trip.trip_id == trip_id)
        .values(
            end_time=end_time,
            end_lat=end_lat,
            end_lng=end_lng,
            crash_detected=crash_detected,
            status="completed",
            updated_at=datetime.utcnow(),
        )
    )


async def cancel_trip(db: AsyncSession, trip_id: str) -> None:
    """Force-cancel a trip (if aborted)."""
    await db.execute(
        update(Trip)
        .where(Trip.trip_id == trip_id)
        .values(status="cancelled", updated_at=datetime.utcnow())
    )


# -------------------------------
# FETCHING TRIPS
# -------------------------------

async def get_active_trip_for_device(db: AsyncSession, device_id: str) -> Optional[Trip]:
    """
    Return the currently active trip (recording) for a given device.
    Used when telemetry arrives without a trip_id.
    """
    res = await db.execute(
        select(Trip)
        .where(Trip.device_id == device_id, Trip.status == "recording")
        .order_by(Trip.start_time.desc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def get_trip_by_id(db: AsyncSession, trip_id: str) -> Optional[Trip]:
    """Fetch a trip by its ID."""
    res = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    return res.scalar_one_or_none()


async def list_trips_for_user(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Trip]:
    """List trips for a user (for history screens)."""
    q = (
        select(Trip)
        .where(Trip.user_id == user_id)
        .order_by(Trip.start_time.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(q)
    return tuple(res.scalars().all())




# | Function                       | What it does                                                                          | Used by              |
# | ------------------------------ | ------------------------------------------------------------------------------------- | -------------------- |
# | `create_trip()`                | Creates a new trip when a `trip_start` arrives (sets status=recording).               | persistence worker   |
# | `close_trip()`                 | Marks a trip as completed on `trip_end`.                                              | persistence worker   |
# | `cancel_trip()`                | Cancels a trip (for errors or user aborts).                                           | optional admin route |
# | `get_active_trip_for_device()` | Finds the open trip for a helmet; used when telemetry arrives but no trip_id is sent. | persistence worker   |
# | `get_trip_by_id()`             | Fetches a single trip by ID (for APIs or debugging).                                  | API route            |
# | `list_trips_for_user()`        | Lists all trips for a specific user (used for history pages).                         | `/api/v1/trips`      |

from app.models.db_models import TripData

class TripsRepo:
    """
    Static wrapper class for better import usage in endpoints.
    """
    @staticmethod
    async def get_trip(db: AsyncSession, trip_id: str) -> Optional[Trip]:
        return await get_trip_by_id(db, trip_id)

    @staticmethod
    async def get_user_trips(db: AsyncSession, user_id: str, limit: int = 50, offset: int = 0) -> Sequence[Trip]:
        return await list_trips_for_user(db, user_id, limit, offset)

    @staticmethod
    async def get_trip_route_points(db: AsyncSession, trip_id: str) -> Sequence[TripData]:
        """
        Fetch GPS points for a trip, ordered by time.
        Only returns points with valid lat/lng.
        """
        q = (
            select(TripData)
            .where(
                TripData.trip_id == trip_id,
                TripData.lat.is_not(None),
                TripData.lng.is_not(None)
            )
            .order_by(TripData.timestamp.asc())
        )
        res = await db.execute(q)
        return tuple(res.scalars().all())

    @staticmethod
    async def get_last_known_location(db: AsyncSession, trip_id: str) -> Optional[TripData]:
        """
        Fetch the most recent TripData with valid lat/lng for a trip.
        Used to set end_lat/end_lng when auto-closing.
        """
        q = (
            select(TripData)
            .where(
                TripData.trip_id == trip_id,
                TripData.lat.is_not(None),
                TripData.lng.is_not(None)
            )
            .order_by(TripData.timestamp.desc())
            .limit(1)
        )
        res = await db.execute(q)
        return res.scalar_one_or_none()

