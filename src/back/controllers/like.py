from sqlalchemy.ext.asyncio import AsyncSession
from repositories.like_repository import LikeRepository
from repositories.track_repository import TrackRepository
from repositories.playlist_repository import PlaylistRepository
from fastapi import HTTPException
from models.user import User


class LikeController:
    @staticmethod
    async def like_track(db: AsyncSession, track_id: int, user: User):
        track = await TrackRepository.get_by_id(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        already_liked = await LikeRepository.is_liked(db, user.idUser, track_id)
        if already_liked:
            raise HTTPException(status_code=409, detail="Track already liked")

        await LikeRepository.like_track(db, user.idUser, track_id)

        liked_playlist = await LikeRepository.get_or_create_liked_playlist(
            db, user.idUser
        )
        await PlaylistRepository.add_track(
            db, track.title, track.youtubeLink, liked_playlist.idPlaylist
        )

        return {"trackId": track_id, "isLiked": True}

    @staticmethod
    async def unlike_track(db: AsyncSession, track_id: int, user: User):
        track = await TrackRepository.get_by_id(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        removed = await LikeRepository.unlike_track(db, user.idUser, track_id)
        if not removed:
            raise HTTPException(status_code=404, detail="Track not liked")

        liked_playlist = await LikeRepository.get_liked_playlist(db, user.idUser)
        if liked_playlist:
            await PlaylistRepository.remove_track(
                db, liked_playlist.idPlaylist, track_id
            )
            remaining_likes = await LikeRepository.get_liked_track_ids(db, user.idUser)
            if len(remaining_likes) == 0:
                await PlaylistRepository.delete(db, liked_playlist)

        return {"trackId": track_id, "isLiked": False}

    @staticmethod
    async def get_like_status(db: AsyncSession, track_id: int, user: User):
        is_liked = await LikeRepository.is_liked(db, user.idUser, track_id)
        return {"trackId": track_id, "isLiked": is_liked}
