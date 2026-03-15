from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.artist import Artist
from typing import Optional, List


class ArtistRepository:
    @staticmethod
    async def create(db: AsyncSession, artist_name: str) -> Artist:
        artist = await ArtistRepository.get_by_name(db, artist_name)
        if not artist:
            artist = Artist(name=artist_name)
            db.add(artist)
            await db.commit()
            await db.refresh(artist)
        return artist

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Artist]:
        result = await db.execute(select(Artist))
        artists: List[Artist] = result.scalars().all()
        return artists

    @staticmethod
    async def get_by_id(db: AsyncSession, artist_id: int) -> Optional[Artist]:
        result = await db.execute(select(Artist).filter(Artist.idArtist == artist_id))
        artist: Optional[Artist] = result.scalars().first()
        return artist

    @staticmethod
    async def get_by_name(db: AsyncSession, artist_name: str) -> Optional[Artist]:
        result = await db.execute(select(Artist).filter(Artist.name == artist_name))
        artist: Optional[Artist] = result.scalars().first()
        return artist
