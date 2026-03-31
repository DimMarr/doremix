from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from models.track import Track
from models.artist import Artist


class TrackRepository:
    @staticmethod
    async def create(db: AsyncSession, track: Track) -> Track:
        db.add(track)
        await db.commit()
        await db.refresh(track)
        return track

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Track]:
        result = await db.execute(select(Track))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, track_id: int) -> Track | None:
        result = await db.execute(select(Track).filter(Track.idTrack == track_id))
        return cast(Track | None, result.scalars().first())

    @staticmethod
    async def get_by_youtube_link(db: AsyncSession, youtube_link: str) -> Track | None:
        result = await db.execute(
            select(Track).filter(Track.youtubeLink == youtube_link)
        )
        return cast(Track | None, result.scalars().first())

    @staticmethod
    async def get_by_artist(db: AsyncSession, artist_id: int) -> list[Track]:
        result = await db.execute(
            select(Track)
            .join(Track.artists)
            .options(joinedload(Track.artists))
            .filter(Artist.idArtist == artist_id)
        )
        return list(result.unique().scalars().all())

    @staticmethod
    async def search_tracks(
        db: AsyncSession, query: str, limit: int = 10
    ) -> list[Track]:
        result = await db.execute(
            select(Track)
            .outerjoin(Track.artists)
            .options(joinedload(Track.artists))
            .filter(
                or_(
                    Track.title.ilike(f"%{query}%"),
                    Artist.name.ilike(f"%{query}%"),
                )
            )
            .distinct()
            .limit(limit)
        )
        return list(result.unique().scalars().all())
