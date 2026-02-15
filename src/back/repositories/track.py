from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.engine import Result
from typing import Optional, List, cast

from models import Track, Artist


class TrackRepository:
    @staticmethod
    async def create(db: AsyncSession, track: Track) -> Track:
        db.add(track)
        await db.commit()
        await db.refresh(track)
        return track

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Track]:
        result: Result[tuple[Track]] = await db.execute(
            select(Track).options(selectinload(Track.artists))
        )
        return cast(List[Track], result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, track_id: int) -> Optional[Track]:
        result: Result[tuple[Track]] = await db.execute(
            select(Track)
            .where(Track.idTrack == track_id)
            .options(selectinload(Track.artists))
        )
        return cast(Optional[Track], result.scalars().first())

    @staticmethod
    async def get_by_youtube_link(
        db: AsyncSession, youtube_link: str
    ) -> Optional[Track]:
        result: Result[tuple[Track]] = await db.execute(
            select(Track)
            .where(Track.youtubeLink == youtube_link)
            .options(selectinload(Track.artists))
        )
        return cast(Optional[Track], result.scalars().first())

    @staticmethod
    async def search_tracks(
        db: AsyncSession, query: str, limit: int = 10
    ) -> List[Track]:
        result: Result[tuple[Track]] = await db.execute(
            select(Track)
            .join(Track.artists)
            .options(joinedload(Track.artists))
            .where(
                or_(
                    Track.title.ilike(f"%{query}%"),
                    Artist.name.ilike(f"%{query}%"),
                )
            )
            .distinct()
            .limit(limit)
        )
        return cast(List[Track], result.scalars().all())
