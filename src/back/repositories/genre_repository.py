from typing import Optional, cast
from models.genre import Genre
from sqlalchemy.orm import Session
from sqlalchemy import func


class GenreRepository:
    @staticmethod
    def get_all(db: Session) -> list[Genre]:
        return cast(list[Genre], db.query(Genre).all())

    @staticmethod
    def get_by_id(db: Session, genre_id: int) -> Optional[Genre]:
        return cast(
            Optional[Genre],
            db.query(Genre).filter(Genre.idGenre == genre_id).first(),
        )

    @staticmethod
    def get_by_label(db: Session, label: str) -> Optional[Genre]:
        return cast(
            Optional[Genre],
            db.query(Genre).filter(func.lower(Genre.label) == label.lower()).first(),
        )

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
