from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from controllers import TrackController
from schemas import TrackSchema
from database import get_db

router = APIRouter(prefix="/tracks", tags=["Tracks"])


# =========================
# GET routes
# =========================
@router.get(
    "/",
    response_model=List[TrackSchema],
    summary="List all tracks",
    description="Returns the complete list of available tracks.",
)
async def get_tracks(db: AsyncSession = Depends(get_db)):
    tracks = await TrackController.get_all_tracks(db)
    return tracks


@router.get(
    "/by-url",
    response_model=TrackSchema,
    summary="Get a track by URL",
    description="Returns the detailed information of a track based on its YouTube URL.",
)
async def get_track_by_url(url: str, db: AsyncSession = Depends(get_db)):
    track = await TrackController.get_track_by_url(db, url)
    return track


@router.get(
    "/{track_id}",
    response_model=TrackSchema,
    summary="Get a track by ID",
    description="Returns the detailed information of a track based on its ID.",
)
async def get_track(track_id: int, db: AsyncSession = Depends(get_db)):
    track = await TrackController.get_track(db, track_id)
    return track
