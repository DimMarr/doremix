from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from repositories import ArtistRepository


class ArtistController:
    @staticmethod
    async def get_all_artists(db: AsyncSession):
        artists = await ArtistRepository.get_all(db)
        if not artists:
            raise HTTPException(status_code=404, detail="No artists found")
        return artists

    @staticmethod
    async def get_artist(db: AsyncSession, artist_id: int):
        artist = await ArtistRepository.get_by_id(db, artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        return artist

    @staticmethod
    async def get_artist_tracks(db: AsyncSession, artist_id: int):
        from repositories.track_repository import TrackRepository

        artist = await ArtistRepository.get_by_id(db, artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        tracks = await TrackRepository.get_by_artist(db, artist_id)
        return tracks
