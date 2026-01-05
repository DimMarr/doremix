from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Playlist, Track
from typing import Optional, List
from sqlalchemy.orm import noload, selectinload


class PlaylistRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Playlist]:
        playlists = await db.execute(
            select(Playlist)
            .options(
                selectinload(Playlist.tracks)
                .selectinload(Track.artists)
            )
        )
        return playlists.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, playlist_id: int) -> Optional[Playlist]:
        playlist = await db.execute(
            select(Playlist)
            .where(Playlist.idPlaylist == playlist_id)
            .options(
                selectinload(Playlist.tracks)
                .selectinload(Track.artists)
            )
        )
        return playlist.scalars().first()
    

