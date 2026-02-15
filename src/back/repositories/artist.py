from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from typing import Optional, List, cast

from models import Artist


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
        result: Result[tuple[Artist]] = await db.execute(select(Artist))
        return cast(List[Artist], result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, artist_id: int) -> Optional[Artist]:
        result: Result[tuple[Artist]] = await db.execute(
            select(Artist).where(Artist.idArtist == artist_id)
        )
        return cast(Optional[Artist], result.scalars().first())

    @staticmethod
    async def get_by_name(db: AsyncSession, artist_name: str) -> Optional[Artist]:
        result: Result[tuple[Artist]] = await db.execute(
            select(Artist).where(Artist.name == artist_name)
        )
        return cast(Optional[Artist], result.scalars().first())
