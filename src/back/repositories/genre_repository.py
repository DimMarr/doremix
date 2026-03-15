from typing import Optional, cast
from models.genre import Genre
from models.playlist import Playlist
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class GenreRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Genre]:
        result = await db.execute(select(Genre))
        return cast(list[Genre], result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, genre_id: int) -> Optional[Genre]:
        result = await db.execute(select(Genre).filter(Genre.idGenre == genre_id))
        return cast(Optional[Genre], result.scalars().first())

    @staticmethod
    async def create(db: AsyncSession, label: str) -> Genre:
        genre = Genre(label=label)
        db.add(genre)
        await db.commit()
        await db.refresh(genre)
        return genre

    @staticmethod
    async def update(db: AsyncSession, genre_id: int, label: str) -> Optional[Genre]:
        genre = await GenreRepository.get_by_id(db, genre_id)
        if not genre:
            return None
        genre.label = label
        await db.commit()
        await db.refresh(genre)
        return genre

    @staticmethod
    async def delete(db: AsyncSession, genre_id: int) -> tuple[bool, str]:
        genre = await GenreRepository.get_by_id(db, genre_id)
        if not genre:
            return False, "not_found"

        # Check FK constraint: any playlist still using this genre?
        result = await db.execute(select(Playlist).filter(Playlist.idGenre == genre_id))
        in_use = result.scalars().first()
        if in_use:
            return False, "in_use"

        await db.delete(genre)
        await db.commit()
        return True, "deleted"
