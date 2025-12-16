from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from controllers import PlaylistController
from schemas import PlaylistSchema, TrackSchema
from database import get_db

router = APIRouter(prefix='/playlists', tags=['Playlists'])

@router.get(
    "/",
    response_model=List[PlaylistSchema],
    summary="Lister toutes les playlists",
    description="Retourne la liste complète des playlists disponibles."
)
def get_playlists(db: Session = Depends(get_db)):
    playlists = PlaylistController.get_all_playlists(db)
    return playlists

@router.get(
    '/{idPlaylist}',
    response_model=PlaylistSchema,
    summary="Récupérer une playlist",
    description="Retourne les informations détaillées d'une playlist à partir de son identifiant."
)
def get_playlist(idPlaylist: int, db: Session = Depends(get_db)):
    playlist = PlaylistController.get_playlist(db, idPlaylist)
    return playlist

@router.get(
    '/{idPlaylist}/tracks',
    response_model=List[TrackSchema],
    summary="Récupérer les pistes d'une playlist",
    description="Retourne la liste des pistes associées à une playlist spécifique."
    )
def get_playlist_tracks(idPlaylist: int, db: Session = Depends(get_db)):
    tracks = PlaylistController.get_playlist_tracks(db, idPlaylist)
    return tracks