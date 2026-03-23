from typing import cast
from models.genre import Genre
from models.playlist import Playlist
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func


class GenreRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Genre]:
        result = await db.execute(select(Genre))
        return cast(list[Genre], result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, genre_id: int) -> Genre | None:
        result = await db.execute(select(Genre).filter(Genre.idGenre == genre_id))
        return cast(Genre | None, result.scalars().first())

    @staticmethod
    async def get_by_label(db: AsyncSession, label: str) -> Genre | None:
        result = await db.execute(
            select(Genre).filter(func.lower(Genre.label) == label.lower())
        )
        return cast(Genre | None, result.scalars().first())

    @staticmethod
    async def create(db: AsyncSession, label: str) -> Genre:
        genre = Genre(label=label)
        db.add(genre)
        await db.commit()
        await db.refresh(genre)
        return genre

    @staticmethod
    async def update(db: AsyncSession, genre_id: int, label: str) -> Genre | None:
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
        result = await db.execute(select(Playlist).filter(Playlist.idGenre == genre_id))
        if result.scalars().first():
            return False, "in_use"
        await db.delete(genre)
        await db.commit()
        return True, "deleted"
