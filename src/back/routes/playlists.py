from models.user import User
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from controllers import PlaylistController
from schemas import (
    PlaylistSchema,
    TrackSchema,
    PlaylistCreate,
    PlaylistUpdate,
    SharePlaylistRequest,
    ShareGroupRequest,
)
from database import get_db
import os

from middleware.auth_middleware import get_current_user, get_current_user_id

router = APIRouter(prefix="/playlists", tags=["Playlists"])


class AddTrackBody(BaseModel):
    url: str
    title: str


@router.post(
    "/",
    response_model=PlaylistSchema,
    summary="Créer une playlist",
    description="Crée une nouvelle playlist avec les informations fournies.",
)
def create_playlist(
    playlist: PlaylistCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return PlaylistController.create_playlist(db, playlist.model_dump(), user_id)


@router.get(
    "/",
    response_model=List[PlaylistSchema],
    summary="Lister toutes les playlists accessibles par l'utilisateur courrant",
    description="Retourne la liste complète des playlists visibles.",
)
def get_accessible_playlists(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    playlists = PlaylistController.get_accessible_playlists(db, user_id)
    return playlists


@router.get(
    "/public",
    response_model=List[PlaylistSchema],
    summary="Lister toutes les playlists publiques",
    description="Retourne la liste complète des playlists disponibles.",
)
def get_public_playlists(db: Session = Depends(get_db)):
    playlists = PlaylistController.get_public_playlists(db)
    return playlists


@router.get(
    "/{idPlaylist}",
    response_model=PlaylistSchema,
    summary="Récupérer une playlist",
    description="Retourne les informations détaillées d'une playlist à partir de son identifiant.",
)
def get_playlist(idPlaylist: int, db: Session = Depends(get_db)):
    playlist = PlaylistController.get_playlist(db, idPlaylist)
    return playlist


@router.get("/{playlist_id}/tracks", response_model=List[TrackSchema])
def get_playlist_tracks(playlist_id: int, db: Session = Depends(get_db)):
    tracks = PlaylistController.get_playlist_tracks(db, playlist_id)
    return tracks


@router.post(
    "/{playlist_id}/tracks/by-url",
    response_model=TrackSchema,
    summary="Ajoute un track à une playlist via URL (Sécurisé)",
)
def add_playlist_track_by_url(
    playlist_id: int,
    body: AddTrackBody,
    db: Session = Depends(get_db),
    user_id: User = Depends(get_current_user_id),
):
    track = PlaylistController.add_playlist_track_secure(
        db, body.title, body.url, playlist_id, user_id
    )

    if not track:
        raise HTTPException(status_code=500, detail="Failed to add track")
    return track


@router.post("/{playlist_id}/cover", response_model=PlaylistSchema)
def upload_playlist_cover(
    playlist_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    updated_playlist = PlaylistController.upload_cover(db, playlist_id, file)
    return updated_playlist


@router.get("/covers/{filename}")
def get_cover_image(filename: str):
    filepath = f"/app/uploads/covers/{filename}"

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath)


@router.delete(
    "/{playlist_id}",
    response_model=dict,
    summary="Delete a playlist",
    description="Deletes a playlist by its ID.",
)
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    # TODO: Quand l'auth sera en place :
    # def delete_playlist(playlist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.delete_playlist(db, playlist_id, current_user.id)

    return PlaylistController.delete_playlist(db, playlist_id)


@router.delete("/{playlist_id}/track/{track_id}", response_model=PlaylistSchema)
def remove_track(playlist_id: int, track_id: int, db: Session = Depends(get_db)):
    updated_playlist = PlaylistController.remove_track(db, playlist_id, track_id)

    return updated_playlist


@router.patch(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Update a playlist",
    description="Updates a playlist by its ID.",
)
def update_playlist(
    playlist_id: int, playlist_data: PlaylistUpdate, db: Session = Depends(get_db)
):
    # TODO: Quand l'auth sera en place :
    # def update_playlist(playlist_id: int, playlist_data: PlaylistUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.update_playlist(db, playlist_id, playlist_data.model_dump(exclude_unset=True), current_user.id)

    return PlaylistController.update_playlist(
        db, playlist_id, playlist_data.model_dump(exclude_unset=True)
    )


@router.post("/{playlist_id}/share/user", summary="Partager avec un utilisateur")
def share_playlist_user(
    playlist_id: int, req: SharePlaylistRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
    
):
    return PlaylistController.share_user(
        db, playlist_id, user_id, req.target_email, req.is_editor
    )


@router.post("/{playlist_id}/share/group", summary="Partager avec un groupe")
def share_playlist_group(
    playlist_id: int, req: ShareGroupRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    return PlaylistController.share_group(
        db, playlist_id, user_id, req.group_name
    )
