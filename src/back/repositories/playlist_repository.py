from sqlalchemy.orm import Session
from models import Playlist
from models.track_playlist import TrackPlaylist
from models.track import Track
from models.artist import Artist
from models.user_playlists import UserPlaylist
from typing import Optional, List
from repositories.track_repository import TrackRepository
from repositories.artist_repository import ArtistRepository
from utils.youtube_utils import get_youtube_video_duration, get_youtube_video_author, get_youtube_video_info


class PlaylistRepository:
    @staticmethod
    def get_all(db: Session) -> List[Playlist]:
        return db.query(Playlist).all()

    @staticmethod
    def get_by_id(db: Session, playlist_id: int) -> Optional[Playlist]:
        return db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()

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
            durationSeconds, author_name = get_youtube_video_info(youtubeLink)

            if durationSeconds is None:
                durationSeconds = 0
            if author_name is None:
                author_name = "Unknown Artist"

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
        return db.query(Playlist).filter(Playlist.name == name).all()

    @staticmethod
    def update_playlist(db: Session, playlist: Playlist, update_data: dict) -> Playlist:
        for key, value in update_data.items():
            if value is not None:
                setattr(playlist, key, value)
        db.commit()
        db.refresh(playlist)
        return playlist