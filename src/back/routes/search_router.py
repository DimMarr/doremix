from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from controllers import PlaylistController, TrackController
from database import get_db

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
def search(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db)
):
    tracks = TrackController.search(db, q)
    playlists = PlaylistController.search(db, q)
    
    return {
        "tracks": tracks,
        "playlists": playlists
    }