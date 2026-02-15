from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db

from controllers import PlaylistController
from schemas import (
    PlaylistSchema,
    TrackSchema,
    PlaylistCreate,
    PlaylistUpdate,
    TrackCreate,
)

router = APIRouter(prefix="/playlists", tags=["Playlists"])


# =========================
# GET routes
# =========================
@router.get(
    "/",
    response_model=List[PlaylistSchema],
    summary="List all playlists",
    description="Returns the complete list of available playlists.",
)
async def get_playlists(db: AsyncSession = Depends(get_db)):
    playlists = await PlaylistController.get_all_playlists(db)
    return playlists


@router.get(
    "/public",
    response_model=List[PlaylistSchema],
    summary="List all public playlists",
    description="Returns the complete list of available public playlists.",
)
async def get_public_playlists(db: AsyncSession = Depends(get_db)):
    playlists = await PlaylistController.get_public_playlists(db)
    return playlists


@router.get(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Get a playlist by ID",
    description="Returns the detailed information of a playlist based on its ID.",
)
async def get_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    playlist = await PlaylistController.get_playlist(db, playlist_id)
    return playlist


@router.get(
    "/{playlist_id}/tracks",
    response_model=List[TrackSchema],
    summary="Get playlist tracks",
    description="Returns the list of tracks associated with a playlist.",
)
async def get_playlist_tracks(playlist_id: int, db: AsyncSession = Depends(get_db)):
    tracks = await PlaylistController.get_playlist_tracks(db, playlist_id)
    return tracks


# =========================
# POST routes
# =========================
@router.post(
    "/",
    response_model=PlaylistSchema,
    summary="Create a new playlist",
    description="Creates a new playlist with the provided data.",
)
async def create_playlist(playlist: PlaylistCreate, db: AsyncSession = Depends(get_db)):
    return await PlaylistController.create_playlist(db, playlist)
    # TODO: Quand l'auth sera en place :
    # def create_playlist(playlist: PlaylistCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.create_playlist(db, playlist.model_dump(), current_user)


@router.post(
    "/{playlist_id}/tracks",
    response_model=TrackSchema,
    summary="Add a track to a playlist",
    description="Adds a track to a playlist by its ID.",
)
async def add_playlist_track_by_url(
    playlist_id: int,
    track: TrackCreate,
    db: AsyncSession = Depends(get_db),
):
    track = await PlaylistController.add_playlist_track(db, track, playlist_id)
    return track


# =========================
# DELETE routes
# =========================
@router.delete(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Delete a playlist",
    description="Deletes a playlist by its ID.",
)
async def delete_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    return await PlaylistController.delete_playlist(db, playlist_id)
    # TODO: Quand l'auth sera en place :
    # def delete_playlist(playlist_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.delete_playlist(db, playlist_id, current_user.id)


@router.delete(
    "/{playlist_id}/track/{track_id}",
    response_model=PlaylistSchema,
    summary="Remove a track from a playlist",
    description="Removes a track from a playlist by its ID.",
)
async def remove_track(
    playlist_id: int, track_id: int, db: AsyncSession = Depends(get_db)
):
    updated_playlist = await PlaylistController.remove_track(db, playlist_id, track_id)
    return updated_playlist


# =========================
# UPDATE routes
# =========================
@router.patch(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Update a playlist",
    description="Updates a playlist by its ID.",
)
async def update_playlist(
    playlist_id: int, playlist: PlaylistUpdate, db: AsyncSession = Depends(get_db)
):
    update_playlist = await PlaylistController.update_playlist(
        db, playlist_id, playlist
    )
    return update_playlist
    # TODO: Quand l'auth sera en place :
    # def update_playlist(playlist_id: int, playlist_data: PlaylistUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.update_playlist(db, playlist_id, playlist_data.model_dump(exclude_unset=True), current_user.id)


@router.post(
    "/{playlist_id}/cover",
    response_model=PlaylistSchema,
    summary="Upload a cover image for a playlist",
    description="Uploads a cover image for a playlist by its ID.",
)
async def upload_playlist_cover(
    playlist_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    updated_playlist = await PlaylistController.upload_cover(db, playlist_id, file)
    return updated_playlist
