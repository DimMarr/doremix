from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from repositories import GenreRepository
from models import Genre


class GenreController:
    @staticmethod
    async def get_all_genres(db: AsyncSession) -> list[Genre]:
        genres = await GenreRepository.get_all(db)
        if not genres:
            raise HTTPException(status_code=404, detail="No genres found")
        return genres

    @staticmethod
    async def get_genre(db: AsyncSession, genre_id: int) -> Genre | None:
        genre = await GenreRepository.get_by_id(db, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")
        return genre

    @staticmethod
    async def create_genre(db: AsyncSession, label: str) -> Genre:
        if await GenreRepository.get_by_label(db, label):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Genre already exists",
            )
        return await GenreRepository.create(db, label)

    @staticmethod
    async def update_genre(db: AsyncSession, genre_id: int, label: str) -> Genre:
        existing = await GenreRepository.get_by_label(db, label)
        if existing and existing.idGenre != genre_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Genre already exists",
            )
        genre = await GenreRepository.update(db, genre_id, label)
        if not genre:
            raise HTTPException(status_code=404, detail=f"Genre {genre_id} not found")
        return genre

    @staticmethod
    async def delete_genre(db: AsyncSession, genre_id: int) -> bool:
        deleted, reason = await GenreRepository.delete(db, genre_id)
        if not deleted:
            if reason == "not_found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre {genre_id} not found",
                )
            if reason == "in_use":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete genre: it is still used by one or more playlists",
                )
        return deleted
