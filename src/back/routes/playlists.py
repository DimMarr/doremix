from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from controllers import PlaylistController
from schemas import PlaylistSchema
from database import get_db

router = APIRouter(prefix='/playlists', tags=['Playlists'])

@router.get('/', response_model=List[PlaylistSchema])
def get_playlists(db: Session = Depends(get_db)):
    playlists = PlaylistController.get_all_playlists(db)
    return playlists

@router.get('/{playlist_id}', response_model=PlaylistSchema)
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = PlaylistController.get_playlist(db, playlist_id)
    return playlist

#@router.get('/{playlist_id}/tracks', response_model=List[TrackSchema])