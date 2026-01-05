from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Track
from typing import Optional, List
from sqlalchemy.orm import noload, selectinload

class TrackRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Track]:
        result = await db.execute(
            select(Track).options(selectinload(Track.artists))
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, track_id: int) -> Optional[Track]:
        result = await db.execute(
            select(Track).filter(Track.idTrack == track_id).options(selectinload(Track.artists))
            )
        return result.scalars().first()