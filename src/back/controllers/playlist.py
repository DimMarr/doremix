from sqlalchemy.orm import Session
from repositories import PlaylistRepository
from fastapi import HTTPException, UploadFile, Response
from utils.image_processor import save_cover_image


class PlaylistController:
    @staticmethod
    def get_all_playlists(db: Session):
        return PlaylistRepository.get_all(db)

    @staticmethod
    def get_playlist(db: Session, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    @staticmethod
    def get_playlist_tracks(db: Session, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist.tracks

    @staticmethod
    def add_playlist_track(
        db: Session,
        title: str,
        youtubeLink: str,
        playlist_id: int,
    ):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return PlaylistRepository.add_track(db, title, youtubeLink, playlist_id)

    @staticmethod
    def upload_cover(db: Session, playlist_id: int, file: UploadFile):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        cover_path = save_cover_image(file, playlist_id)

        updated_playlist = PlaylistRepository.update_cover_image(
            db, playlist_id, cover_path
        )

        return updated_playlist

    @staticmethod
    def remove_track(db: Session, playlist_id: int, track_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not PlaylistRepository.remove_track(db, playlist_id, track_id):
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )

        db.refresh(playlist)

        return playlist
