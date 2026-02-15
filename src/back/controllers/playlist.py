from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile, Response
from fastapi.responses import JSONResponse

from utils.image_processor import save_cover_image

from repositories import PlaylistRepository
from models import Playlist, Track
from schemas import PlaylistCreate, PlaylistUpdate, TrackCreate


class PlaylistController:
    # =========================
    # GET methods
    # =========================
    @staticmethod
    async def get_all_playlists(db: AsyncSession):
        playlists = await PlaylistRepository.get_all(db)
        if not playlists:
            raise HTTPException(status_code=404, detail="Playlists not found")
        return playlists

    @staticmethod
    async def get_public_playlists(db: AsyncSession):
        playlists = await PlaylistRepository.get_public_playlists(db)
        if not playlists:
            raise HTTPException(status_code=404, detail="Public playlists not found")
        return playlists

    @staticmethod
    async def get_playlist(db: AsyncSession, playlist_id: int):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    @staticmethod
    async def get_playlist_tracks(db: AsyncSession, playlist_id: int):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist.tracks

    @staticmethod
    def search(db: AsyncSession, query: str):
        if not query or len(query) < 2:
            raise HTTPException(
                status_code=400, detail="Query must be at least 2 characters"
            )

        playlists = PlaylistRepository.search_playlists(db, query)
        return playlists

    # =========================
    # CREATE methods
    # =========================
    @staticmethod
    async def add_playlist_track(
        db: AsyncSession, track_create: TrackCreate, playlist_id: int
    ) -> Track:
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        new_track = Track(**track_create.model_dump())
        track_obj, track_status = await PlaylistRepository.add_track(
            db, new_track, playlist_id
        )

        # Gérer les erreurs
        if track_status == "invalid_url":
            raise HTTPException(status_code=403, detail="Invalid YouTube URL provided")
        if track_status == "failed" or track_obj is None:
            raise HTTPException(status_code=400, detail="Failed to add track")
        if track_status == "already_exists":
            raise HTTPException(
                status_code=409, detail="Track already exists in this playlist"
            )

        return track_obj

        # TODO: Quand l'auth sera en place, vérifier les permissions :
        # is_owner = playlist.idOwner == user_id
        # is_editor = PlaylistRepository.is_user_editor(db, playlist.idPlaylist, user_id)
        # is_open = playlist.visibility.value == "OPEN"

    @staticmethod
    async def create_playlist(db: AsyncSession, playlist: PlaylistCreate):
        new_playlist = Playlist(
            **playlist.model_dump(),
            idOwner=1,  # TODO: Remplacer par current_user.id quand l'auth sera en place
        )
        return await PlaylistRepository.create(db, new_playlist)

    # =========================
    # DELETE methods
    # =========================
    @staticmethod
    async def delete_playlist(db: AsyncSession, playlist_id: int):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        deleted = await PlaylistRepository.delete(db, playlist)
        return deleted
        # TODO: Quand l'auth sera en place, vérifier que l'utilisateur est le propriétaire :
        # if playlist.idOwner != user_id:
        #     raise HTTPException(status_code=403, detail="You are not the owner of this playlist")

    @staticmethod
    async def remove_track(db: AsyncSession, playlist_id: int, track_id: int):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        removed = await PlaylistRepository.remove_track(db, playlist_id, track_id)
        if not removed:
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )
        await db.refresh(playlist)
        return playlist

    # =========================
    # UPDATE methods
    # =========================
    @staticmethod
    async def update_playlist(
        db: AsyncSession, playlist_id: int, update_data: PlaylistUpdate
    ):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        return await PlaylistRepository.update(db, playlist, update_data)

        # TODO: Quand l'auth sera en place, vérifier que l'utilisateur est le propriétaire :
        # if playlist.idOwner != user_id:
        #     raise HTTPException(status_code=403, detail="You are not the owner of this playlist")

    @staticmethod
    def upload_cover(db: AsyncSession, playlist_id: int, file: UploadFile):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        cover_path = save_cover_image(file, playlist_id)

        updated_playlist = PlaylistRepository.update_cover_image(
            db, playlist_id, cover_path
        )

        return updated_playlist
