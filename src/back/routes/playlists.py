from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from controllers import PlaylistController
from schemas import PlaylistSchema, TrackSchema
from database import get_db
import os

router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.get(
    "/",
    response_model=List[PlaylistSchema],
    summary="Lister toutes les playlists",
    description="Retourne la liste complète des playlists disponibles.",
)
async def get_playlists(db: Session = Depends(get_db)):
    playlists = await PlaylistController.get_all_playlists(db)
    return playlists


@router.get(
    "/{idPlaylist}",
    response_model=PlaylistSchema,
    summary="Récupérer une playlist",
    description="Retourne les informations détaillées d'une playlist à partir de son identifiant.",
)
async def get_playlist(idPlaylist: int, db: Session = Depends(get_db)):
    playlist = await PlaylistController.get_playlist(db, idPlaylist)
    return playlist


@router.get("/{playlist_id}/tracks", response_model=List[TrackSchema])
async def get_playlist_tracks(playlist_id: int, db: Session = Depends(get_db)):
    tracks = await PlaylistController.get_playlist_tracks(db, playlist_id)
    return tracks


@router.post("/{playlist_id}/cover", response_model=PlaylistSchema)
async def upload_playlist_cover(
    playlist_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    updated_playlist = await PlaylistController.upload_cover(db, playlist_id, file)
    return updated_playlist


@router.get("/covers/{filename}")
async def get_cover_image(filename: str):
    filepath = f"/app/uploads/covers/{filename}"

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath)


@router.delete("/{playlist_id}/track/{track_id}", response_model=PlaylistSchema)
def remove_track(playlist_id: int, track_id: int, db: Session = Depends(get_db)):
    updated_playlist = PlaylistController.remove_track(db, playlist_id, track_id)

    return updated_playlist
