from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from controllers.admin_playlist_controller import AdminPlaylistController
from schemas import PlaylistSchema, TrackSchema, PlaylistUpdate
from database import get_db
from middleware.auth_middleware import require_role

router = APIRouter(prefix="/admin/playlists", tags=["Admin Playlists"])


class AddTrackBody(BaseModel):
    url: str
    title: str


@router.get(
    "/",
    response_model=List[PlaylistSchema],
    summary="List all playlists",
    description="Returns all playlists regardless of visibility. Admin only.",
)
def get_all_playlists(
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return AdminPlaylistController.get_all(db)


@router.get(
    "/{playlist_id}/tracks",
    response_model=List[TrackSchema],
    summary="Get tracks of any playlist",
    description="Returns all tracks of a playlist. Admin only.",
)
def get_playlist_tracks(
    playlist_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return AdminPlaylistController.get_tracks(db, playlist_id)


@router.patch(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Update any playlist",
    description="Updates name, genre, or visibility of any playlist. Admin only.",
)
def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return AdminPlaylistController.update_playlist(
        db, playlist_id, playlist_data.model_dump(exclude_unset=True)
    )


@router.delete(
    "/{playlist_id}",
    response_model=dict,
    summary="Delete any playlist",
    description="Deletes any playlist. Admin only.",
)
def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return AdminPlaylistController.delete_playlist(db, playlist_id)


@router.post(
    "/{playlist_id}/tracks/by-url",
    response_model=TrackSchema,
    summary="Add track to any playlist",
    description="Adds a track via YouTube URL to any playlist. Admin only.",
)
def add_track(
    playlist_id: int,
    body: AddTrackBody,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return AdminPlaylistController.add_track(db, playlist_id, body.title, body.url)


@router.delete(
    "/{playlist_id}/track/{track_id}",
    response_model=PlaylistSchema,
    summary="Remove track from any playlist",
    description="Removes a track from any playlist. Admin only.",
)
def remove_track(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return AdminPlaylistController.remove_track(db, playlist_id, track_id)
