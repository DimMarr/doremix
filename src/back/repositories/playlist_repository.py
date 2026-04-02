from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, exists
from re import findall as regex_match
from models.playlist import Playlist, PlaylistVisibility
from models.playlist_vote import PlaylistVote
from models.track_playlist import TrackPlaylist
from models.track import Track
from models.user_playlists import UserPlaylist
from models.user import User, UserRole
from models.group import GroupUser, GroupPlaylist, UserGroup
from repositories.track_repository import TrackRepository
from repositories.artist_repository import ArtistRepository
from utils.youtube_utils import get_youtube_video_info
import asyncio


class PlaylistRepository:
    @staticmethod
    def _attach_user_vote(playlist: Playlist, user_vote: int | None) -> Playlist:
        setattr(playlist, "userVote", user_vote)
        return playlist

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
            select(Playlist, PlaylistVote.value)
            .options(joinedload(Playlist.genre))
            .outerjoin(
                PlaylistVote,
                and_(
                    PlaylistVote.idPlaylist == Playlist.idPlaylist,
                    PlaylistVote.idUser == user_id,
                ),
            )
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
        return [
            PlaylistRepository._attach_user_vote(playlist, user_vote)
            for playlist, user_vote in result.all()
        ]

    @staticmethod
    async def get_public_playlists(db: AsyncSession, user: User) -> list[Playlist]:
        result = await db.execute(
            select(Playlist, PlaylistVote.value)
            .options(joinedload(Playlist.genre))
            .outerjoin(
                PlaylistVote,
                and_(
                    PlaylistVote.idPlaylist == Playlist.idPlaylist,
                    PlaylistVote.idUser == user.idUser,
                ),
            )
            .filter(
                Playlist.visibility == PlaylistVisibility.PUBLIC,
                Playlist.idOwner != user.idUser,
                ~exists().where(UserPlaylist.idPlaylist == Playlist.idPlaylist),
            )
        )
        return [
            PlaylistRepository._attach_user_vote(playlist, user_vote)
            for playlist, user_vote in result.all()
        ]

    @staticmethod
    async def get_shared_playlist(db: AsyncSession, user_id: int) -> list[Playlist]:
        direct_shared_subquery = select(UserPlaylist.idPlaylist).filter(
            UserPlaylist.idUser == user_id
        )
        my_group_ids = select(GroupUser.idGroup).filter(GroupUser.idUser == user_id)
        group_shared_subquery = select(GroupPlaylist.idPlaylist).filter(
            GroupPlaylist.idGroup.in_(my_group_ids)
        )

        result = await db.execute(
            select(Playlist, PlaylistVote.value)
            .outerjoin(
                PlaylistVote,
                and_(
                    PlaylistVote.idPlaylist == Playlist.idPlaylist,
                    PlaylistVote.idUser == user_id,
                ),
            )
            .filter(
                or_(
                    Playlist.idPlaylist.in_(direct_shared_subquery),
                    Playlist.idPlaylist.in_(group_shared_subquery),
                )
            )
            .distinct()
        )
        return [
            PlaylistRepository._attach_user_vote(playlist, user_vote)
            for playlist, user_vote in result.all()
        ]

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
                select(Playlist, PlaylistVote.value)
                .options(joinedload(Playlist.genre))
                .outerjoin(
                    PlaylistVote,
                    and_(
                        PlaylistVote.idPlaylist == Playlist.idPlaylist,
                        PlaylistVote.idUser == user_id,
                    ),
                )
                .filter(Playlist.idPlaylist == playlist_id)
            )
            row = result.first()
            if not row:
                return None
            playlist, user_vote = row
            return PlaylistRepository._attach_user_vote(playlist, user_vote)

        result = await db.execute(
            select(Playlist, PlaylistVote.value)
            .options(joinedload(Playlist.genre))
            .outerjoin(
                PlaylistVote,
                and_(
                    PlaylistVote.idPlaylist == Playlist.idPlaylist,
                    PlaylistVote.idUser == user_id,
                ),
            )
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
        row = result.first()
        if not row:
            return None
        playlist, user_vote = row
        return PlaylistRepository._attach_user_vote(playlist, user_vote)

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
        result = await db.execute(select(Playlist).options(joinedload(Playlist.genre)))
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
        track_to_remove = result.scalars().first()
        if track_to_remove:
            prev_result = await db.execute(
                select(TrackPlaylist).filter(
                    TrackPlaylist.idPlaylist == playlist_id,
                    TrackPlaylist.next_track_id == track_id,
                )
            )
            prev_track = prev_result.scalars().first()
            if prev_track:
                prev_track.next_track_id = track_to_remove.next_track_id
            await db.delete(track_to_remove)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_playlist_tracks(db: AsyncSession, playlist_id: int) -> list[Track]:
        result = await db.execute(
            select(Track, TrackPlaylist)
            .join(TrackPlaylist, TrackPlaylist.idTrack == Track.idTrack)
            .filter(TrackPlaylist.idPlaylist == playlist_id)
        )
        rows = result.all()
        if not rows:
            return []

        node_map = {
            row.Track.idTrack: (row.Track, row.TrackPlaylist.next_track_id)
            for row in rows
        }
        next_ids = {
            row.TrackPlaylist.next_track_id
            for row in rows
            if row.TrackPlaylist.next_track_id is not None
        }

        head_id = None
        for track_id in node_map:
            if track_id not in next_ids:
                head_id = track_id
                break

        if head_id is None:
            head_id = rows[0].Track.idTrack

        ordered_tracks = []
        current_id = head_id
        visited = set()

        while (
            current_id is not None
            and current_id in node_map
            and current_id not in visited
        ):
            visited.add(current_id)
            track, next_id = node_map[current_id]
            ordered_tracks.append(track)
            current_id = next_id

        for track_id, (track, _) in node_map.items():
            if track_id not in visited:
                ordered_tracks.append(track)

        return ordered_tracks

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
            duration_seconds, author_name, channel_url = await asyncio.to_thread(
                get_youtube_video_info, clean_url
            )

            if author_name == "Video unavailable":
                return track, "invalid url"

            if duration_seconds is None:
                duration_seconds = 0
            if author_name is None:
                author_name = "Unknown Artist"

            artist = await ArtistRepository.create(
                db, author_name, channel_url=channel_url
            )

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

        track_playlist = TrackPlaylist(
            idPlaylist=playlist_id, idTrack=track.idTrack, next_track_id=None
        )
        db.add(track_playlist)
        await db.flush()

        last_track_result = await db.execute(
            select(TrackPlaylist).filter(
                TrackPlaylist.idPlaylist == playlist_id,
                TrackPlaylist.next_track_id.is_(None),
                TrackPlaylist.idTrack != track.idTrack,
            )
        )
        last_track = last_track_result.scalars().first()
        if last_track:
            last_track.next_track_id = track.idTrack

        await db.commit()
        await db.refresh(track_playlist)
        return track, "added"

    @staticmethod
    async def move_track(
        db: AsyncSession, playlist_id: int, track_id: int, prev_track_id: int | None
    ) -> bool:
        result = await db.execute(
            select(TrackPlaylist).filter(
                TrackPlaylist.idPlaylist == playlist_id,
                TrackPlaylist.idTrack == track_id,
            )
        )
        track_to_move = result.scalars().first()
        if not track_to_move:
            return False

        current_prev_result = await db.execute(
            select(TrackPlaylist).filter(
                TrackPlaylist.idPlaylist == playlist_id,
                TrackPlaylist.next_track_id == track_id,
            )
        )
        current_prev = current_prev_result.scalars().first()

        if current_prev:
            current_prev.next_track_id = track_to_move.next_track_id

        if prev_track_id is None:
            all_links_result = await db.execute(
                select(TrackPlaylist.idTrack, TrackPlaylist.next_track_id).filter(
                    TrackPlaylist.idPlaylist == playlist_id
                )
            )
            all_links = all_links_result.all()
            pointed_to = {
                link.next_track_id
                for link in all_links
                if link.next_track_id is not None and link.idTrack != track_id
            }
            current_head_id = None
            for link in all_links:
                if link.idTrack != track_id and link.idTrack not in pointed_to:
                    current_head_id = link.idTrack
                    break
            track_to_move.next_track_id = current_head_id
        else:
            target_prev_result = await db.execute(
                select(TrackPlaylist).filter(
                    TrackPlaylist.idPlaylist == playlist_id,
                    TrackPlaylist.idTrack == prev_track_id,
                )
            )
            target_prev = target_prev_result.scalars().first()
            if not target_prev:
                return False
            track_to_move.next_track_id = target_prev.next_track_id
            target_prev.next_track_id = track_to_move.idTrack

        await db.commit()
        return True

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

        if owner_id is None:
            return [], "You're not allowed to see shared users for this playlist"

        current_user_result = await db.execute(
            select(User).filter(User.idUser == current_user_id)
        )

        current_user = current_user_result.scalars().first()
        is_admin = current_user is not None and current_user.idRole == 3

        if (
            not is_admin
            and current_user_id != owner_id
            and current_user_id not in [u.idUser for u in users]
        ):
            return [], "You're not allowed to see shared users for this playlist"

        return users, None

    @staticmethod
    async def list_shared_groups(
        db: AsyncSession, playlist_id: int, current_user_id: int
    ):
        # Check playlist owner
        owner_result = await db.execute(
            select(Playlist.idOwner).filter(Playlist.idPlaylist == playlist_id)
        )
        owner_id = owner_result.scalar()

        if owner_id is None:
            return [], "You're not allowed to see shared groups for this playlist"

        current_user_result = await db.execute(
            select(User).filter(User.idUser == current_user_id)
        )
        current_user = current_user_result.scalars().first()
        is_admin = current_user is not None and current_user.idRole == 3

        if not is_admin and current_user_id != owner_id:
            return [], "You're not allowed to see shared groups for this playlist"

        result = await db.execute(
            select(UserGroup)
            .join(GroupPlaylist, GroupPlaylist.idGroup == UserGroup.idGroup)
            .filter(GroupPlaylist.idPlaylist == playlist_id)
        )
        groups = result.scalars().all()
        return groups, None

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
        if existing_result.scalars().first():
            return True, "already_shared"

        link = GroupPlaylist(idGroup=group.idGroup, idPlaylist=playlist_id)
        db.add(link)
        await db.commit()

        return True, "success"

    @staticmethod
    async def remove_shared_user(
        db: AsyncSession, playlist_id: int, target_user_id: int
    ) -> bool:
        link_result = await db.execute(
            select(UserPlaylist).filter(
                UserPlaylist.idPlaylist == playlist_id,
                UserPlaylist.idUser == target_user_id,
            )
        )
        link = link_result.scalars().first()
        if not link:
            return False
        await db.delete(link)
        await db.commit()
        return True

    @staticmethod
    async def transfer_ownership(
        db: AsyncSession, playlist_id: int, current_owner_id: int, new_owner_email: str
    ) -> Playlist | None:
        result = await db.execute(
            select(Playlist).filter(Playlist.idPlaylist == playlist_id)
        )
        playlist = cast(Playlist | None, result.scalars().first())
        if not playlist or playlist.idOwner != current_owner_id:
            return None

        user_result = await db.execute(
            select(User).filter(User.email == new_owner_email)
        )
        new_owner = cast(User | None, user_result.scalars().first())
        if not new_owner:
            return None

        playlist.idOwner = new_owner.idUser
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def remove_shared_group(
        db: AsyncSession, playlist_id: int, target_group_id: int
    ) -> bool:
        link_result = await db.execute(
            select(GroupPlaylist).filter(
                GroupPlaylist.idPlaylist == playlist_id,
                GroupPlaylist.idGroup == target_group_id,
            )
        )
        link = link_result.scalars().first()
        if not link:
            return False
        await db.delete(link)
        await db.commit()
        return True
