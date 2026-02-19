from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from controllers import PlaylistController, TrackController
from database import get_db
from middleware.auth_middleware import get_current_user_id


router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db),
    idUser: int = Depends(get_current_user_id),
):
    tracks = TrackController.search(db, q, idUser)
    playlists = PlaylistController.search(db, q, idUser)

    return {"tracks": tracks, "playlists": playlists}
