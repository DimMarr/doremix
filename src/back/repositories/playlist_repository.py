from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, exists
from re import findall as regex_match
from models.playlist import Playlist, PlaylistVisibility
from models.track_playlist import TrackPlaylist
from models.track import Track
from models.artist import Artist
from models.user_playlists import UserPlaylist
from models.user import User, UserRole
from models.group import GroupUser, GroupPlaylist, UserGroup
from typing import Optional, List
from repositories.track_repository import TrackRepository
from repositories.artist_repository import ArtistRepository
from utils.youtube_utils import (
    get_youtube_video_duration,
    get_youtube_video_author,
    get_youtube_video_info,
)


class PlaylistRepository:
    # get_all() supprimée pour la notion d'accès

    # Toutes les playlists auxquelles l'utilisateur a accès
    @staticmethod
    def get_accessible_playlists(db: Session, user_id: int) -> List[Playlist]:
        # Playlists partagées avec l'utilisateur
        direct_shared_subquery = db.query(UserPlaylist.idPlaylist).filter(
            UserPlaylist.idUser == user_id
        )

        # Playlists partagées via les GROUPES
        my_group_ids = db.query(GroupUser.idGroup).filter(GroupUser.idUser == user_id)
        group_shared_subquery = db.query(GroupPlaylist.idPlaylist).filter(
            GroupPlaylist.idGroup.in_(my_group_ids)
        )

        playlists: List[Playlist] = (
            db.query(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(
                or_(
                    Playlist.idOwner == user_id,
                    Playlist.visibility == PlaylistVisibility.PUBLIC,
                    Playlist.visibility == PlaylistVisibility.OPEN,
                    Playlist.idOwner is None,
                    Playlist.idPlaylist.in_(direct_shared_subquery),
                    Playlist.idPlaylist.in_(group_shared_subquery),
                )
            )
            .distinct()
            .all()
        )

        return playlists

    # Toutes les playlists publiques qui n'appartiennent pas à l'utilisateur
    @staticmethod
    def get_public_playlists(db: Session, user: User) -> List[Playlist]:
        playlists: List[Playlist] = (
            db.query(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(Playlist.visibility == PlaylistVisibility.PUBLIC)
            .filter(Playlist.idOwner != user.idUser)
            .filter(~exists().where(UserPlaylist.idPlaylist == Playlist.idPlaylist))
            .all()
        )
        return playlists

    # Toutes les playlists partagées à l'utilisateur
    @staticmethod
    def get_shared_playlist(db: Session, user_id: int):
        playlists: List[Playlist] = (
            db.query(Playlist)
            .filter(UserPlaylist.idPlaylist == Playlist.idPlaylist)
            .filter(UserPlaylist.idUser == user_id)
            .all()
        )
        return playlists

    @staticmethod
    def get_by_id(db: Session, playlist_id: int, user: User) -> Optional[Playlist]:
        user_id = user.idUser
        user_role = user.role
        direct_shared_subquery = db.query(UserPlaylist.idPlaylist).filter(
            UserPlaylist.idUser == user_id
        )

        my_group_ids = db.query(GroupUser.idGroup).filter(GroupUser.idUser == user_id)
        group_shared_subquery = db.query(GroupPlaylist.idPlaylist).filter(
            GroupPlaylist.idGroup.in_(my_group_ids)
        )

        playlist: Optional[Playlist] = (
            db.query(Playlist)
            .options(joinedload(Playlist.genre))
            .filter(Playlist.idPlaylist == playlist_id)
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
            .first()
        )

        if user_role == UserRole.ADMIN:
            playlist = (
                db.query(Playlist)
                .options(joinedload(Playlist.genre))
                .filter(Playlist.idPlaylist == playlist_id)
                .first()
            )

        return playlist

    @staticmethod
    def create(db: Session, playlist: Playlist) -> Playlist:
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist

    @staticmethod
    def update(db: Session, playlist: Playlist) -> Playlist:
        db.commit()
        db.refresh(playlist)
        return playlist

    @staticmethod
    def delete(db: Session, playlist: Playlist) -> None:
        db.delete(playlist)
        db.commit()

    @staticmethod
    def update_cover_image(
        db: Session, playlist_id: int, cover_path: str
    ) -> Optional[Playlist]:
        playlist: Optional[Playlist] = (
            db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        )
        if playlist:
            playlist.coverImage = cover_path
            db.commit()
            db.refresh(playlist)
        return playlist

    @staticmethod
    def remove_track(db: Session, playlist_id: int, track_id: int) -> bool:
        track = (
            db.query(TrackPlaylist)
            .filter(TrackPlaylist.idPlaylist == playlist_id)
            .filter(TrackPlaylist.idTrack == track_id)
            .first()
        )

        if track:
            db.delete(track)
            db.commit()
            return True
        if track:
            db.delete(track)
            db.commit()
            return True
        return False

    @staticmethod
    def get_playlist_tracks(db: Session, playlist_id: int) -> List[Track]:
        tracks: List[Track] = (
            db.query(Track)
            .join(TrackPlaylist)
            .filter(TrackPlaylist.idPlaylist == playlist_id)
            .order_by(TrackPlaylist.idTrack)
            .all()
        )
        return tracks

    @staticmethod
    def add_track(
        db: Session,
        title: str,
        youtubeLink: str,
        playlist_id: int,
    ):
        track = TrackRepository.get_by_youtube_link(db, youtubeLink)

        # Search for https://www.youtube.com/watch?=***** or https://youtu.be/***** URL format
        match = regex_match(
            r"(https://www\.youtube\.com/watch\?v=[^&|\s]+|https://youtu\.be/[^?|\s]+)",
            youtubeLink,
        )
        if not match:
            return track, "invalid url"
        else:
            clean_url = match[0]

        # If track doesn't already exists in DB, get infos
        if not track:
            durationSeconds, author_name = get_youtube_video_info(clean_url)

            # Checks if Youtube video exists
            if author_name == "Video unavailable":
                return track, "invalid url"

            if durationSeconds is None:
                durationSeconds = 0
            if author_name is None:
                author_name = "Unknown Artist"

            artist = ArtistRepository.create(db, author_name)

            track = TrackRepository.create(
                db,
                Track(
                    title=title,
                    youtubeLink=clean_url,
                    durationSeconds=durationSeconds,
                    artists=[artist],
                ),
            )
            if not track:
                return None

        existing = (
            db.query(TrackPlaylist)
            .filter(TrackPlaylist.idPlaylist == playlist_id)
            .filter(TrackPlaylist.idTrack == track.idTrack)
            .first()
        )
        if existing:
            return track, "already_exists"

        trackPlaylist = TrackPlaylist(idPlaylist=playlist_id, idTrack=track.idTrack)
        db.add(trackPlaylist)
        db.commit()
        db.refresh(trackPlaylist)
        return track, "added"

    @staticmethod
    def get_by_name(db: Session, name: str) -> List[Playlist]:
        playlists: List[Playlist] = (
            db.query(Playlist).filter(Playlist.name == name).all()
        )
        return playlists

    @staticmethod
    def update_playlist(db: Session, playlist: Playlist, update_data: dict) -> Playlist:
        for key, value in update_data.items():
            if value is not None:
                setattr(playlist, key, value)
        db.commit()
        db.refresh(playlist)
        return playlist

    @staticmethod
    def search_playlists(
        db: Session, query: str, idUser: int, limit: int = 10
    ) -> List[Playlist]:
        playlists: List[Playlist] = (
            db.query(Playlist)
            .filter(
                and_(
                    Playlist.name.ilike(f"%{query}%"),
                    or_(
                        Playlist.visibility == PlaylistVisibility.PUBLIC,
                        Playlist.visibility == PlaylistVisibility.OPEN,
                        Playlist.idOwner == idUser,
                        exists().where(
                            and_(
                                UserPlaylist.idPlaylist == Playlist.idPlaylist,
                                UserPlaylist.idUser == idUser,
                            )
                        ),
                    ),
                )
            )
            .limit(limit)
            .all()
        )
        return playlists

    @staticmethod
    def can_edit_playlist(db: Session, playlist_id: int, user_id: int) -> bool:
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        if not playlist:
            return False

        if playlist.idOwner == user_id:
            return True

        if playlist.visibility == PlaylistVisibility.PUBLIC:
            return True

        # Gestion du droit le plus fort
        direct_right = (
            db.query(UserPlaylist)
            .filter(
                UserPlaylist.idPlaylist == playlist_id,
                UserPlaylist.idUser == user_id,
                UserPlaylist.editor,
            )
            .all()
        )

        print(direct_right)
        if direct_right:
            return True

        return False

    @staticmethod
    def list_shared_user(db: Session, playlist_id: int, current_user_id: int):
        users = (
            db.query(UserPlaylist).filter(UserPlaylist.idPlaylist == playlist_id).all()
        )
        if current_user_id != db.query(Playlist.idOwner).filter(
            Playlist.idPlaylist == playlist_id
        ).scalar() and current_user_id not in [
            user_playlist.idUser for user_playlist in users
        ]:
            return [], "You're not allowed to see shared users for this playlist"
        if users:
            return users, None
        else:
            return [], None

    @staticmethod
    def share_with_user(
        db: Session, playlist_id: int, owner_id: int, target_email: str, is_editor: bool
    ):
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()

        if not playlist or playlist.idOwner != owner_id:
            return False, "forbidden"

        target = db.query(User).filter(User.email == target_email).first()
        if not target:
            return False, "user_not_found"

        if target.idUser == owner_id:
            return False, "self_share"

        link = UserPlaylist(
            idUser=target.idUser, idPlaylist=playlist_id, editor=is_editor
        )
        db.merge(link)
        db.commit()
        return True, "success"

    @staticmethod
    def share_with_group(db: Session, playlist_id: int, owner_id: int, group_name: str):
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()

        if not playlist or playlist.idOwner != owner_id:
            return False, "forbidden"

        group = db.query(UserGroup).filter(UserGroup.groupName == group_name).first()
        if not group:
            return False, "group_not_found"

        # Vérifier si déjà partagé pour éviter erreur SQL (Primary Key)
        exists = (
            db.query(GroupPlaylist)
            .filter(
                GroupPlaylist.idGroup == group.idGroup,
                GroupPlaylist.idPlaylist == playlist_id,
            )
            .first()
        )

        if not exists:
            link = GroupPlaylist(idGroup=group.idGroup, idPlaylist=playlist_id)
            db.add(link)
            db.commit()

        return True, "success"
