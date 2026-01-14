from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from models.playlist import Playlist, PlaylistVisibility
from models.track_playlist import TrackPlaylist
from models.track import Track
from models.artist import Artist
from typing import Optional, List
from repositories.track_repository import TrackRepository
from repositories.artist_repository import ArtistRepository
from utils.youtube_utils import get_youtube_video_duration, get_youtube_video_author


class PlaylistRepository:
    @staticmethod
    def get_all(db: Session) -> List[Playlist]:
        return db.query(Playlist).all()

    @staticmethod
    def get_by_id(db: Session, playlist_id: int) -> Optional[Playlist]:
        return db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()

    @staticmethod
    def create(db: Session, playlist_data: dict) -> Playlist:
        new_playlist = Playlist(**playlist_data)
        db.add(new_playlist)
        db.commit()
        db.refresh(new_playlist)

        return new_playlist

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
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
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
        return False

    @staticmethod
    def add_track(
        db: Session,
        title: str,
        youtubeLink: str,
        playlist_id: int,
    ):
        track = TrackRepository.get_by_youtube_link(db, youtubeLink)

        if not track:
            durationSeconds = get_youtube_video_duration(youtubeLink)
            author_name = get_youtube_video_author(youtubeLink)
            if durationSeconds is None:
                durationSeconds = 0

            artist = ArtistRepository.create(db, author_name)

            track = TrackRepository.create(
                db,
                Track(
                    title=title,
                    youtubeLink=youtubeLink,
                    durationSeconds=durationSeconds,
                    artists=[artist],
                ),
            )
            if not track:
                return None

        trackPlaylist = TrackPlaylist(idPlaylist=playlist_id, idTrack=track.idTrack)
        db.add(trackPlaylist)
        db.commit()
        db.refresh(trackPlaylist)
        return trackPlaylist and track

    @staticmethod
    def search_playlists(db: Session, query: str, limit: int = 10) -> List[Playlist]:
        playlists = (
            db.query(Playlist)
            .options(joinedload(Playlist.owner))
            .filter(
                and_(
                    Playlist.name.ilike(f"%{query}%"),
                    or_(
                        Playlist.visibility == PlaylistVisibility.PUBLIC,
                        Playlist.visibility == PlaylistVisibility.OPEN,
                    ),
                )
            )
            .limit(limit)
            .all()
        )
        return playlists
