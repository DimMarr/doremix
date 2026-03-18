from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, exists
from re import findall as regex_match
from models.playlist import Playlist, PlaylistVisibility
from models.track_playlist import TrackPlaylist
from models.track import Track
from models.artist import Artist
from models.user_playlists import UserPlaylist
from models.user import User, UserRole
from models.group import GroupUser, GroupPlaylist, UserGroup
from repositories.track_repository import TrackRepository
from repositories.artist_repository import ArtistRepository
from utils.youtube_utils import get_youtube_video_info


class PlaylistRepository:
    @staticmethod
    async def get_accessible_playlists(
        db: AsyncSession, user_id: int
    ) -> list[Playlist]:
        direct_shared_subquery = select(UserPlaylist.idPlaylist).filter(
            UserPlaylist.idUser == user_id
        )
        my_group_ids = select(GroupUser.idGroup).filter(GroupUser.idUser == user_id)
        group_shared_subquery = select(GroupPlaylist.idPlaylist).filter(
            GroupPlaylist.idGroup.in_(my_group_ids)
        )
        result = await db.execute(
            select(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(
                or_(
                    Playlist.idOwner == user_id,
                    Playlist.visibility == PlaylistVisibility.PUBLIC,
                    Playlist.visibility == PlaylistVisibility.OPEN,
                    Playlist.idOwner.is_(None),
                    Playlist.idPlaylist.in_(direct_shared_subquery),
                    Playlist.idPlaylist.in_(group_shared_subquery),
                )
            )
            .distinct()
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_public_playlists(db: AsyncSession, user: User) -> list[Playlist]:
        result = await db.execute(
            select(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(
                Playlist.visibility == PlaylistVisibility.PUBLIC,
                Playlist.idOwner != user.idUser,
                ~exists().where(UserPlaylist.idPlaylist == Playlist.idPlaylist),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_shared_playlist(db: AsyncSession, user_id: int) -> list[Playlist]:
        result = await db.execute(
            select(Playlist)
            .join(UserPlaylist, UserPlaylist.idPlaylist == Playlist.idPlaylist)
            .filter(UserPlaylist.idUser == user_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(
        db: AsyncSession, playlist_id: int, user: User
    ) -> Playlist | None:
        user_id = user.idUser
        direct_shared_subquery = select(UserPlaylist.idPlaylist).filter(
            UserPlaylist.idUser == user_id
        )
        my_group_ids = select(GroupUser.idGroup).filter(GroupUser.idUser == user_id)
        group_shared_subquery = select(GroupPlaylist.idPlaylist).filter(
            GroupPlaylist.idGroup.in_(my_group_ids)
        )

        if user.role == UserRole.ADMIN:
            result = await db.execute(
                select(Playlist)
                .options(joinedload(Playlist.genre))
                .filter(Playlist.idPlaylist == playlist_id)
            )
            return cast(Playlist | None, result.scalars().first())

        result = await db.execute(
            select(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(
                Playlist.idPlaylist == playlist_id,
                or_(
                    Playlist.idOwner == user_id,
                    Playlist.visibility == PlaylistVisibility.PUBLIC,
                    Playlist.visibility == PlaylistVisibility.OPEN,
                    Playlist.idOwner.is_(None),
                    Playlist.idPlaylist.in_(direct_shared_subquery),
                    Playlist.idPlaylist.in_(group_shared_subquery),
                ),
            )
        )
        return cast(Playlist | None, result.scalars().first())

    @staticmethod
    async def get_by_id_raw(db: AsyncSession, playlist_id: int) -> Playlist | None:
        result = await db.execute(
            select(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(Playlist.idPlaylist == playlist_id)
        )
        return cast(Playlist | None, result.scalars().first())

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Playlist]:
        """Admin-only: returns all playlists regardless of visibility."""
        result = await db.execute(
            select(Playlist).options(joinedload(Playlist.genre))
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, playlist: Playlist) -> Playlist:
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def update(db: AsyncSession, playlist: Playlist) -> Playlist:
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def delete(db: AsyncSession, playlist: Playlist) -> None:
        await db.delete(playlist)
        await db.commit()

    @staticmethod
    async def update_cover_image(
        db: AsyncSession, playlist_id: int, cover_path: str
    ) -> Playlist | None:
        result = await db.execute(
            select(Playlist).filter(Playlist.idPlaylist == playlist_id)
        )
        playlist = cast(Playlist | None, result.scalars().first())
        if playlist:
            playlist.coverImage = cover_path
            await db.commit()
            await db.refresh(playlist)
        return playlist

    @staticmethod
    async def remove_track(db: AsyncSession, playlist_id: int, track_id: int) -> bool:
        result = await db.execute(
            select(TrackPlaylist).filter(
                TrackPlaylist.idPlaylist == playlist_id,
                TrackPlaylist.idTrack == track_id,
            )
        )
        track = result.scalars().first()
        if track:
            await db.delete(track)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_playlist_tracks(db: AsyncSession, playlist_id: int) -> list[Track]:
        result = await db.execute(
            select(Track)
            .join(TrackPlaylist)
            .filter(TrackPlaylist.idPlaylist == playlist_id)
            .order_by(TrackPlaylist.idTrack)
        )
        return list(result.scalars().all())

    @staticmethod
    async def add_track(
        db: AsyncSession, title: str, youtubeLink: str, playlist_id: int
    ):
        track = await TrackRepository.get_by_youtube_link(db, youtubeLink)

        match = regex_match(
            r"(https://www\.youtube\.com/watch\?v=[^&|\s]+|https://youtu\.be/[^?|\s]+)",
            youtubeLink,
        )
        if not match:
            return track, "invalid url"
        clean_url = match[0]

        if not track:
            duration_seconds, author_name = get_youtube_video_info(clean_url)

            if author_name == "Video unavailable":
                return track, "invalid url"

            if duration_seconds is None:
                duration_seconds = 0
            if author_name is None:
                author_name = "Unknown Artist"

            artist = await ArtistRepository.create(db, author_name)
            track = await TrackRepository.create(
                db,
                Track(
                    title=title,
                    youtubeLink=clean_url,
                    durationSeconds=duration_seconds,
                    artists=[artist],
                ),
            )
            if not track:
                return None

        result = await db.execute(
            select(TrackPlaylist).filter(
                TrackPlaylist.idPlaylist == playlist_id,
                TrackPlaylist.idTrack == track.idTrack,
            )
        )
        if result.scalars().first():
            return track, "already_exists"

        track_playlist = TrackPlaylist(idPlaylist=playlist_id, idTrack=track.idTrack)
        db.add(track_playlist)
        await db.commit()
        await db.refresh(track_playlist)
        return track, "added"

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> list[Playlist]:
        result = await db.execute(select(Playlist).filter(Playlist.name == name))
        return list(result.scalars().all())

    @staticmethod
    async def update_playlist(
        db: AsyncSession, playlist: Playlist, update_data: dict
    ) -> Playlist:
        for key, value in update_data.items():
            if value is not None:
                setattr(playlist, key, value)
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def search_playlists(
        db: AsyncSession, query: str, user_id: int, limit: int = 10
    ) -> list[Playlist]:
        result = await db.execute(
            select(Playlist)
            .filter(
                and_(
                    Playlist.name.ilike(f"%{query}%"),
                    or_(
                        Playlist.visibility == PlaylistVisibility.PUBLIC,
                        Playlist.visibility == PlaylistVisibility.OPEN,
                        Playlist.idOwner == user_id,
                        exists().where(
                            and_(
                                UserPlaylist.idPlaylist == Playlist.idPlaylist,
                                UserPlaylist.idUser == user_id,
                            )
                        ),
                    ),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def can_edit_playlist(
        db: AsyncSession, playlist_id: int, user_id: int
    ) -> bool:
        result = await db.execute(
            select(Playlist).filter(Playlist.idPlaylist == playlist_id)
        )
        playlist = cast(Playlist | None, result.scalars().first())
        if not playlist:
            return False
        if playlist.idOwner == user_id:
            return True
        if playlist.visibility == PlaylistVisibility.PUBLIC:
            return True

        right_result = await db.execute(
            select(UserPlaylist).filter(
                UserPlaylist.idPlaylist == playlist_id,
                UserPlaylist.idUser == user_id,
                UserPlaylist.editor,
            )
        )
        return right_result.scalars().first() is not None

    @staticmethod
    async def list_shared_user(
        db: AsyncSession, playlist_id: int, current_user_id: int
    ):
        users_result = await db.execute(
            select(UserPlaylist).filter(UserPlaylist.idPlaylist == playlist_id)
        )
        users = users_result.scalars().all()

        owner_result = await db.execute(
            select(Playlist.idOwner).filter(Playlist.idPlaylist == playlist_id)
        )
        owner_id = owner_result.scalar()

        if current_user_id != owner_id and current_user_id not in [
            u.idUser for u in users
        ]:
            return [], "You're not allowed to see shared users for this playlist"

        return users, None

    @staticmethod
    async def share_with_user(
        db: AsyncSession,
        playlist_id: int,
        owner_id: int,
        target_email: str,
        is_editor: bool,
    ):
        playlist_result = await db.execute(
            select(Playlist).filter(Playlist.idPlaylist == playlist_id)
        )
        playlist = cast(Playlist | None, playlist_result.scalars().first())
        if not playlist or playlist.idOwner != owner_id:
            return False, "forbidden"

        user_result = await db.execute(select(User).filter(User.email == target_email))
        target = cast(User | None, user_result.scalars().first())
        if not target:
            return False, "user_not_found"
        if target.idUser == owner_id:
            return False, "self_share"

        link = UserPlaylist(
            idUser=target.idUser, idPlaylist=playlist_id, editor=is_editor
        )
        await db.merge(link)
        await db.commit()
        return True, "success"

    @staticmethod
    async def share_with_group(
        db: AsyncSession, playlist_id: int, owner_id: int, group_name: str
    ):
        playlist_result = await db.execute(
            select(Playlist).filter(Playlist.idPlaylist == playlist_id)
        )
        playlist = cast(Playlist | None, playlist_result.scalars().first())
        if not playlist or playlist.idOwner != owner_id:
            return False, "forbidden"

        group_result = await db.execute(
            select(UserGroup).filter(UserGroup.groupName == group_name)
        )
        group = cast(UserGroup | None, group_result.scalars().first())
        if not group:
            return False, "group_not_found"

        existing_result = await db.execute(
            select(GroupPlaylist).filter(
                GroupPlaylist.idGroup == group.idGroup,
                GroupPlaylist.idPlaylist == playlist_id,
            )
        )
        if not existing_result.scalars().first():
            link = GroupPlaylist(idGroup=group.idGroup, idPlaylist=playlist_id)
            db.add(link)
            await db.commit()

        return True, "success"
