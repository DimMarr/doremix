from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from repositories import PlaylistRepository


class AdminPlaylistController:
    @staticmethod
    async def get_all(db: AsyncSession):
        return await PlaylistRepository.get_all(db)

    @staticmethod
    async def get_tracks(db: AsyncSession, playlist_id: int):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return await PlaylistRepository.get_playlist_tracks(db, playlist_id)

    @staticmethod
    async def update_playlist(db: AsyncSession, playlist_id: int, update_data: dict):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return await PlaylistRepository.update_playlist(db, playlist, update_data)

    @staticmethod
    async def delete_playlist(db: AsyncSession, playlist_id: int):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        await PlaylistRepository.delete(db, playlist)
        return {"message": f"Playlist '{playlist.name}' successfully deleted"}

    @staticmethod
    async def add_track(db: AsyncSession, playlist_id: int, title: str, url: str):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        result = await PlaylistRepository.add_track(db, title, url, playlist_id)
        if result is None or not isinstance(result, tuple):
            raise HTTPException(status_code=500, detail="Failed to add track")

        track, status = result
        if status == "invalid url":
            raise HTTPException(status_code=400, detail="Invalid URL")
        if status == "already_exists":
            raise HTTPException(
                status_code=409, detail="Track already exists in this playlist"
            )
        return track

    @staticmethod
    async def remove_track(db: AsyncSession, playlist_id: int, track_id: int):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not await PlaylistRepository.remove_track(db, playlist_id, track_id):
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )
        await db.refresh(playlist)
        return playlist
