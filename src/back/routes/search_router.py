from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from controllers import PlaylistController, TrackController
from database import get_db

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db),
):
    tracks = await TrackController.search(db, q)
    playlists = await PlaylistController.search(db, q)

    return {"tracks": tracks, "playlists": playlists}
