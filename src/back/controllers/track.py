from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from repositories import TrackRepository


class TrackController:
    @staticmethod
    async def get_all_tracks(db: AsyncSession):
        tracks = await TrackRepository.get_all(db)
        if not tracks:
            raise HTTPException(status_code=404, detail="Tracks not found")
        return tracks

    @staticmethod
    async def get_track(db: AsyncSession, track_id: int):
        track = await TrackRepository.get_by_id(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track

    @staticmethod
    async def get_track_by_url(db: AsyncSession, url: str):
        track = await TrackRepository.get_by_youtube_link(db, url)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track

    @staticmethod
    async def search(db: AsyncSession, query: str):
        if not query or len(query) < 2:
            raise HTTPException(
                status_code=400, detail="Query must be at least 2 characters"
            )
        tracks = await TrackRepository.search_tracks(db, query)
        return tracks
