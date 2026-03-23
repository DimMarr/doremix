from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from controllers import PlaylistController, TrackController
from database import get_db
from middleware.auth_middleware import get_current_user_id

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    tracks = await TrackController.search(db, q, user_id)
    playlists = await PlaylistController.search(db, q, user_id)
    return {"tracks": tracks, "playlists": playlists}
