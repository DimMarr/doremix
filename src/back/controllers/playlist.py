from sqlalchemy.ext.asyncio import AsyncSession
from repositories import PlaylistRepository
from models import Playlist
from fastapi import HTTPException, UploadFile, Response
from utils import save_cover_image


class PlaylistController:
    @staticmethod
    async def get_all_playlists(db: AsyncSession):
        return await PlaylistRepository.get_all(db)

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
    async def upload_cover(db: AsyncSession, playlist_id: int, file: UploadFile):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        cover_path = save_cover_image(file, playlist_id)

        updated_playlist = PlaylistRepository.update_cover_image(
            db, playlist_id, cover_path
        )

        return updated_playlist

    @staticmethod
    def remove_track(db: Session, playlist_id: int, track_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not PlaylistRepository.remove_track(db, playlist_id, track_id):
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )

        db.refresh(playlist)

        return playlist
