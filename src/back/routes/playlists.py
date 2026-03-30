from models.user import User
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from controllers import PlaylistController
from schemas import (
    PlaylistSchema,
    TrackSchema,
    PlaylistCreate,
    PlaylistUpdate,
    SharePlaylistRequest,
    ShareGroupRequest,
    TransferPlaylistRequest,
    VoteRequest,
    VoteResponse,
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
    summary="Create a playlist",
    description="Creates a new playlist with the provided information.",
)
async def create_playlist(
    playlist: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await PlaylistController.create_playlist(db, playlist.model_dump(), user_id)


@router.get(
    "/",
    response_model=list[PlaylistSchema],
    summary="List all playlists accessible by the current user",
    description="Returns the complete list of visible playlists.",
)
async def get_accessible_playlists(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await PlaylistController.get_accessible_playlists(db, user_id)


@router.get(
    "/public",
    response_model=list[PlaylistSchema],
    summary="List all public playlists",
    description="Returns the complete list of available public playlists.",
)
async def get_public_playlists(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.get_public_playlists(db, user)


@router.get(
    "/shared",
    summary="List all shared playlists",
    description="Returns the complete list of shared playlists.",
)
async def get_shared_playlists(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await PlaylistController.get_shared_playlists(db, user_id)


@router.get(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Get a playlist",
    description="Returns the detailed information of a playlist based on its ID.",
)
async def get_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.get_playlist(db, playlist_id, user)


@router.put(
    "/{playlist_id}/vote",
    response_model=VoteResponse,
    summary="Cast or remove a playlist vote",
)
async def cast_vote(
    playlist_id: int,
    vote: VoteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.cast_vote(db, playlist_id, vote.value, user)


@router.get(
    "/{playlist_id}/tracks",
    response_model=list[TrackSchema],
    summary="Get playlist tracks",
    description="Returns the list of tracks in a playlist.",
)
async def get_playlist_tracks(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.get_playlist_tracks(db, playlist_id, user)


@router.post(
    "/{playlist_id}/tracks/by-url",
    response_model=TrackSchema,
    summary="Add a track to a playlist via URL (secured)",
)
async def add_playlist_track_by_url(
    playlist_id: int,
    body: AddTrackBody,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await PlaylistController.add_playlist_track_secure(
        db, body.title, body.url, playlist_id, user_id
    )


@router.post(
    "/{playlist_id}/cover",
    response_model=PlaylistSchema,
    summary="Upload a playlist cover image",
)
async def upload_playlist_cover(
    playlist_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.upload_cover(db, playlist_id, file, user)


@router.get(
    "/covers/{filename}",
    summary="Get a cover image",
)
async def get_cover_image(filename: str):
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
async def delete_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.delete_playlist(db, playlist_id, user)


@router.delete(
    "/{playlist_id}/track/{track_id}",
    response_model=PlaylistSchema,
    summary="Remove a track from a playlist",
)
async def remove_track(
    playlist_id: int,
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.remove_track(db, playlist_id, track_id, user)


@router.patch(
    "/{playlist_id}",
    response_model=PlaylistSchema,
    summary="Update a playlist",
    description="Updates a playlist by its ID.",
)
async def update_playlist(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await PlaylistController.update_playlist(
        db, playlist_id, playlist_data.model_dump(exclude_unset=True), user
    )


@router.get(
    "/{playlist_id}/shared-with",
    summary="List users the playlist is shared with and their permissions",
)
async def shared_with(
    playlist_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await PlaylistController.shared_with(db, playlist_id, current_user_id)


@router.post(
    "/{playlist_id}/share/user",
    summary="Share a playlist with a user",
)
async def share_playlist_user(
    playlist_id: int,
    req: SharePlaylistRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await PlaylistController.share_user(
        db, playlist_id, user_id, req.target_email, req.is_editor
    )


@router.post(
    "/{playlist_id}/share/group",
    summary="Share a playlist with a group",
)
async def share_playlist_group(
    playlist_id: int,
    req: ShareGroupRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await PlaylistController.share_group(
        db, playlist_id, user_id, req.group_name
    )


@router.post(
    "/{playlist_id}/transfer",
    response_model=PlaylistSchema,
    summary="Transfer playlist ownership",
    description="Transfers playlist ownership to another user by email. Only the current owner can do this.",
)
async def transfer_playlist(
    playlist_id: int,
    body: TransferPlaylistRequest,
    db: AsyncSession = Depends(get_db),
    owner: User = Depends(get_current_user),
):
    return await PlaylistController.transfer_playlist(
        db, playlist_id, owner, body.new_owner_email
    )
