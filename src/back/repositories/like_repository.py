from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.track_like import TrackLike
from models.playlist import Playlist


class LikeRepository:
    @staticmethod
    async def get_liked_track_ids(db: AsyncSession, user_id: int) -> set[int]:
        result = await db.execute(
            select(TrackLike.idTrack).filter(TrackLike.idUser == user_id)
        )
        return set(result.scalars().all())

    @staticmethod
    async def is_liked(db: AsyncSession, user_id: int, track_id: int) -> bool:
        result = await db.execute(
            select(TrackLike).filter(
                TrackLike.idUser == user_id,
                TrackLike.idTrack == track_id,
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def like_track(db: AsyncSession, user_id: int, track_id: int) -> None:
        like = TrackLike(idUser=user_id, idTrack=track_id)
        await db.merge(like)
        await db.commit()

    @staticmethod
    async def unlike_track(db: AsyncSession, user_id: int, track_id: int) -> bool:
        result = await db.execute(
            select(TrackLike).filter(
                TrackLike.idUser == user_id,
                TrackLike.idTrack == track_id,
            )
        )
        like = result.scalars().first()
        if not like:
            return False
        await db.delete(like)
        await db.commit()
        return True

    @staticmethod
    async def get_liked_playlist(db: AsyncSession, user_id: int) -> Playlist | None:
        result = await db.execute(
            select(Playlist).filter(
                Playlist.idOwner == user_id,
                Playlist.isLikedPlaylist.is_(True),
            )
        )
        return cast(Playlist | None, result.scalars().first())

    @staticmethod
    async def get_or_create_liked_playlist(db: AsyncSession, user_id: int) -> Playlist:
        result = await db.execute(
            select(Playlist).filter(
                Playlist.idOwner == user_id,
                Playlist.isLikedPlaylist.is_(True),
            )
        )
        playlist = cast(Playlist | None, result.scalars().first())
        if playlist:
            return playlist

        new_playlist = Playlist(
            name="Liked Tracks",
            idOwner=user_id,
            isLikedPlaylist=True,
            idGenre=1,
        )
        db.add(new_playlist)
        await db.commit()
        await db.refresh(new_playlist)
        return new_playlist
