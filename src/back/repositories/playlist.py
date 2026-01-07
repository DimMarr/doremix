from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Playlist, Track, TrackPlaylist
from typing import Optional, List
from sqlalchemy.orm import noload, selectinload


class PlaylistRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Playlist]:
        playlists = await db.execute(
            select(Playlist).options(
                selectinload(Playlist.tracks).selectinload(Track.artists)
            )
        )
        return playlists.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, playlist_id: int) -> Optional[Playlist]:
        playlist = await db.execute(
            select(Playlist)
            .where(Playlist.idPlaylist == playlist_id)
            .options(selectinload(Playlist.tracks).selectinload(Track.artists))
        )
        return playlist.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, playlist: Playlist) -> Playlist:
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def update(db: AsyncSession, playlist: Playlist) -> Playlist:
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def delete(db: AsyncSession, playlist: Playlist) -> None:
        await db.delete(playlist)
        await db.commit()

    @staticmethod
    async def update_cover_image(
        db: AsyncSession, playlist_id: int, cover_path: str
    ) -> Optional[Playlist]:
        playlist = await db.execute(
            select(Playlist).filter(Playlist.idPlaylist == playlist_id)
        )
        playlist = playlist.scalars().first()
        if playlist:
            playlist.coverImage = cover_path
            await db.commit()
            await db.refresh(playlist)
        return playlist

    @staticmethod
    async def remove_track(db: AsyncSession, playlist_id: int, track_id: int) -> bool:
        result = await db.execute(
            select(TrackPlaylist)
            .where(TrackPlaylist.idPlaylist == playlist_id)
            .where(TrackPlaylist.idTrack == track_id)
        )
        track = result.scalars().first()

        if track:
            await db.delete(track)
            await db.commit()
            return True
        return False
